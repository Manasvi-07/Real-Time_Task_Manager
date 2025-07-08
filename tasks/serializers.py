from rest_framework import serializers
from .models import Task, TaskAttachment
from accounts.enums import RoleChoices
from rest_framework.exceptions import ValidationError
from .enums import StatusChoices

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'uploaded_at']

class TaskSerializer(serializers.ModelSerializer):
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ['id','title', 'description', 'status',
                  'created_by','assigned_to', 'priority','is_completed',
                  'created_at', 'due_date', 'updated_at', 'attachments']
        
        read_only_fields = ['id','created_by','created_at','updated_at'] 

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
                raise serializers.ValidationError("Invalid status value")
            return value