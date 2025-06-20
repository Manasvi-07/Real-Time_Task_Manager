from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer
from .permissions import RolePermission


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, RolePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Task.objects.all()
        if user.role == 'manager':
            return Task.objects.filter(created_by=user)
        if user.role == 'employee':
            return Task.objects.filter(assigned_to = user)
        return Task.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)