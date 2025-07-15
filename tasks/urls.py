from django.urls import path
from .views import TaskCreateView, TaskListView, TaskDetailView, TaskAttachmentUploadView, TaskStatusUpdateView, TaskReportView

urlpatterns = [
    path('list/', TaskListView.as_view(), name='tasks-list'),
    path('create/', TaskCreateView.as_view(), name='tasks-create'),
    path('detail/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('attachments/<int:task_id>/', TaskAttachmentUploadView.as_view(), name='task-attachment-create'),
    path('update-status/<int:pk>/', TaskStatusUpdateView.as_view(), name='task-status-update'),
    path('reports/',TaskReportView.as_view(), name='task-report'),
]
