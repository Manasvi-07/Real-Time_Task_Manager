from celery import shared_task
from django.core.mail import send_mail
from tasks.models import Task
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings
from .utils import notify_task_update

@shared_task
def send_task_email_notification(task_id):
    try:
        task = Task.objects.select_related('assigned_to').get(id=task_id)

        email = task.assigned_to.email
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

    tasks = Task.objects.select_related('assigned_to').filter(
        is_completed=False,
        assigned_to__isnull=False,
        assigned_to__email__isnull=False,
    )

    count = 0
    for task in tasks:
        email = task.assigned_to.email
        print(f"Sending reminder for task {task.id} to {email}")

        send_mail(
            subject="Reminder: Task Due Soon",
            message=f"Task: {task.title}\n\nDue: {task.due_date.strftime('%Y-%m-%d %H:%M:%S')}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        notify_task_update(task)
        print(f" Reminder email sent and WebSocket notified for task #{task.id}")
        count += 1

    print(f"Reminder task complete. Total reminders sent: {count}")
    return f"Reminders sent for {count} task(s)"