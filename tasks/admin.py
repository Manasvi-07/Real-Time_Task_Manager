from django.contrib import admin
from .models import Task, TaskAttachment

class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'assigned_to',
        'created_by',
        'priority',
        'status',
        'due_date',
        'is_completed',
    )
    list_filter = ('priority', 'status', 'is_completed')
    search_fields = ('title', 'assigned_to__email', 'created_by__email')
    ordering = ('-due_date',)

class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_at', 'file')

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAttachment, TaskAttachmentAdmin)
