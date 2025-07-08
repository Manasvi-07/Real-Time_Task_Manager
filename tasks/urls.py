from django.urls import path
from .views import TaskCreateView, TaskListView, TaskDetailView, TaskAttachmentUploadView, TaskStatusUpdateView, TaskReportView

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='tasks-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/attachments/', TaskAttachmentUploadView.as_view(), name='task-attachment-create'),
    path('tasks/<int:pk>/update-status/', TaskStatusUpdateView.as_view(), name='task-status-update'),
    path('reports/',TaskReportView.as_view(), name='task-report'),
]
