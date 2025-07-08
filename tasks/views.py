from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Task
from django.utils.timezone import now
from django.db.models import Count
from .serializers import TaskSerializer, TaskAttachmentSerializer, TaskStatusUpdateSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied, NotFound
from accounts.enums import RoleChoices
from tasks.tasks import send_task_email_notification, notify_task_update
from django.core.cache import cache

def invalidate_task_cache(task):
    if task.assigned_to:
        cache.delete(f"task_list_user_{task.assigned_to.id}")
    if task.created_by:
        cache.delete(f"task_list_user_{task.created_by.id}")
    
class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        invalidate_task_cache(task)
        send_task_email_notification.delay(task.id)
        notify_task_update(task)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message":"Task Created Successfully", 
            "data":response.data
        }, status=status.HTTP_201_CREATED)

class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        cache_key = f"task_list_user_{user.id}"
        cached_queryset = cache.get(cache_key)
        
        if cached_queryset:
            return cached_queryset
        
        if user.role == RoleChoices.ADMIN:
            queryset =  Task.objects.select_related('assigned_to','created_by').all()
        elif user.role == RoleChoices.MANAGER:
            queryset =  Task.objects.select_related('assigned_to','created_by').filter(created_by=user)
        else:
            queryset =  Task.objects.select_related('assigned_to','created_by').filter(assigned_to=user)

        cache.set(cache_key,queryset,timeout=300)
        return queryset
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()

    def get_object(self):
        task = super().get_object()
        user = self.request.user

        if user.role == RoleChoices.ADMIN:
            return task

        if user.role == RoleChoices.MANAGER:
            if task.created_by == user:
                return task
            raise PermissionDenied("Managers can only access tasks they created.")

        if user.role == RoleChoices.EMPLOYEE:
            if task.assigned_to == user:
                return task
            raise PermissionDenied("Employees can only access tasks assigned to them.")

        raise PermissionDenied("You are not allowed to view this task.")
    
    def get_serializer_class(self):
        """Employees can only update status."""
        user = self.request.user
        if self.request.method in ['PUT', 'PATCH']:
            if user.role == RoleChoices.EMPLOYEE:
                return TaskStatusUpdateSerializer  
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        task = self.get_object()

        if request.user.role == RoleChoices.EMPLOYEE:
            allowed_fields = {'status'}
            if any(field not in allowed_fields for field in request.data):
                raise PermissionDenied("Employees can only update the task status.")
        
        response =  super().update(request, *args, **kwargs)
        invalidate_task_cache(task)
        notify_task_update(task)

        return Response({
            "message":"Tasks Updated Successfully", 
            "data":response.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        invalidate_task_cache(task)
        user = request.user

        if user.role == RoleChoices.ADMIN:
            pass  
        elif user.role == RoleChoices.MANAGER and task.created_by == user:
            pass
        else:
            raise PermissionDenied("You are not allowed to delete this task.")

        response = super().destroy(request, *args, **kwargs)
        return Response({
            "message":"Tasks Delete Successfully", 
            "data":response.data
        }, status=status.HTTP_204_NO_CONTENT)

class TaskAttachmentUploadView(generics.CreateAPIView):
    serializer_class = TaskAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        user = self.request.user
        task_id = self.kwargs.get('task_id')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        if user.role == RoleChoices.ADMIN:
            pass
        
        elif user.role == RoleChoices.MANAGER:
            if task.assigned_to.role != RoleChoices.EMPLOYEE:
                raise PermissionDenied("Managers can only attach files to tasks assigned to employees.")
        
        elif user.role == RoleChoices.EMPLOYEE:
            if task.assigned_to != user:
                raise PermissionDenied("Employees can only attach files to their own tasks.")
        else:
            raise PermissionDenied("You do not have permission to attach files to this task.")
        serializer.save(task=task)

class TaskStatusUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        task = super().get_object()
        user = self.request.user

        if user.role == RoleChoices.ADMIN:
            return task

        elif user.role == RoleChoices.MANAGER and task.created_by == user:
            return task

        elif user.role == RoleChoices.EMPLOYEE and task.assigned_to == user:
            return task

        raise PermissionDenied("You are not allowed to change the status of this task.")
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        task = self.get_object()
        invalidate_task_cache(task)
        notify_task_update(task)
        
        return Response({
            "message": "Task status updated successfully",
            "data": response.data
        }, status=status.HTTP_200_OK)
    
class TaskReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == RoleChoices.ADMIN:
            queryset = Task.objects.all()
        elif user.role == RoleChoices.MANAGER:
            queryset = Task.objects.filter(created_by=user)
        else:
            queryset = Task.objects.filter(assigned_to=user)

        overdue = queryset.filter(is_completed=False, due_date__lt=now()).count()
        completed = queryset.filter(is_completed=True).count()

        productivity = {}
        if user.role == RoleChoices.ADMIN:
            productivity = (
                Task.objects.filter(is_completed=True)
                .values("assigned_to__email", "created_by__email", "id", "status", "title")
                .annotate(total=Count("id"))
            )
        
        return Response({
            "overdue_tasks":overdue,
            "completed_tasks":completed,
            "productivity":productivity
        })
