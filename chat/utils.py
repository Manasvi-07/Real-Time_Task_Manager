from channels.layers import get_channel_layer

async def notify_chat_message(message):
    print("Notifying WebSocket for:", message.to_user.email)
    channel_layer = get_channel_layer()
    from_user = message.from_user
    to_user = message.to_user

    payload = {
        "type": "chat.message",
        "data": {
            "message": message.message,
            "from_user": from_user.id,
            "from_username": from_user.email if from_user else None,
            "from_role": from_user.role if from_user else None,
            "to_user": to_user.id,
            "to_username": to_user.email if to_user else None,
            "to_role": to_user.role if to_user else None,
        },
    }

    for user in [from_user, to_user]:
        group_name = f"user_{user.id}"
        print(f"[WebSocket Notify] Chat message to group: {group_name}")
        await channel_layer.group_send(group_name, payload)
