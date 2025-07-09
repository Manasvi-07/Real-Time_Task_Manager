from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
            "assigned_to": to_user.email if to_user else None,
            "created_by": from_user.email if from_user else None,
        },
    }

    print("Preparing to notify via WebSocket")
    for user in [from_user, to_user]:
        if user:
            group_name = f"user_{user.id}"
            print(f"[Websocket Notify] Sending update to group: {group_name}")
            async_to_sync(channel_layer.group_send)(group_name, payload)
