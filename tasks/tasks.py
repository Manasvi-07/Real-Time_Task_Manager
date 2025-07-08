from celery import shared_task
from django.core.mail import send_mail
from .models import Task
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def send_task_email_notification(task_id):
    try:
        task = Task.objects.select_related('assigned_to').get(id=task_id)
        
        if task.assigned_to and task.assigned_to.email:
            send_mail(
                subject=f"New Task Assigned: {task.title}",
                message=f"{task.description}\n\nDue: {task.due_date.strftime('%Y-%m-%d %H:%M:%S')}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.assigned_to.email],
                fail_silently=False,
            )
            return f"Email sent to {task.assigned_to.email}"
        return "Assigned user has no email"
    
    except Task.DoesNotExist:
        return "Task not found"
  
@shared_task
def daily_task_reminder():
    print("Running daily_task_reminder...")
    tomorrow = now().date() + timedelta(days=1)
    tasks = Task.objects.select_related('assigned_to').filter(
        due_date__date=tomorrow,
        is_completed=False,
        assigned_to__isnull=False,
        assigned_to__email__isnull=False,
    )

    count = 0
    for task in tasks:
        send_mail(
            subject="Reminder: Task Due Tomorrow",
            message=f"Task: {task.title}\n\nDue: {task.due_date.strftime('%Y-%m-%d %H:%M:%S')}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
        )
        count += 1

    return f"Reminders sent for {count} task(s)"

def notify_task_update(task):
    from_user = task.created_by
    to_user = task.assigned_to
    channel_layer = get_channel_layer()

    payload = {
        "type": "task_update",
        "data": {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "assigned_to": to_user.username if to_user else None,
        },
    }

    for user in [from_user, to_user]:
        if user:
            group_name = f"user_{user.id}"
            print(f"Sending update to group: {group_name}")
            async_to_sync(channel_layer.group_send)(group_name, payload)
