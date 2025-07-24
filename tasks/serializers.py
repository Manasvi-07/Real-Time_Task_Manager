from rest_framework import serializers
from .models import Task, TaskAttachment
from accounts.enums import RoleChoices
from rest_framework.exceptions import ValidationError
from .enums import StatusChoices
from accounts.models import CustomUser

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'uploaded_at']

class TaskSerializer(serializers.ModelSerializer):
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=CustomUser.objects.all())
    assigned_to_email = serializers.EmailField(source="assigned_to.email", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    class Meta:
        model = Task
        fields = ['id','title', 'description', 'status',
                  'created_by','assigned_to', 'assigned_to_email', 'created_by_email','priority','is_completed',
                  'created_at', 'due_date', 'updated_at', 'attachments']
        
        read_only_fields = ['id','created_by','created_at','updated_at'] 

    def get_created_by_email(self, obj):
        return getattr(obj.created_by, "email", None)

    def get_assigned_to_email(self, obj):
        return getattr(obj.assigned_to, "email", None)

    def validate_assigned_to(self, value):
        request_user = self.context['request'].user

        if value.role == RoleChoices.ADMIN:
            raise serializers.ValidationError("Tasks cannot be assigned to Admin users.")

        if request_user.role == RoleChoices.MANAGER:
            if value == request_user:
                raise ValidationError("Tasks cannot be assigned to manager users.")
            if value.role != RoleChoices.EMPLOYEE:
                raise ValidationError("Managers can only assign tasks to employees.")
            
        if request_user.role == RoleChoices.EMPLOYEE:
            raise ValidationError("Employees are not allowed to assign tasks.")
            
        return value

class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

    def validate_status(self, value):
        if value not in StatusChoices.values:
            raise serializers.ValidationError("Invalid status value.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        task = self.instance  

        if user.role == RoleChoices.ADMIN:
            return attrs

        elif user.role == RoleChoices.MANAGER:
            if task.created_by != user:
                raise ValidationError("Managers can only update tasks they created.")

        elif user.role == RoleChoices.EMPLOYEE:
            if task.assigned_to != user:
                raise ValidationError("Employees can only update their own tasks.")

        else:
            raise ValidationError("You are not allowed to update task status.")

        return attrs