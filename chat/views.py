from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from .models import chatMessage
from .utils import notify_chat_message
from asgiref.sync import async_to_sync

class ChatMessageSendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from_user = request.user
        to_email = request.data.get("to_email")
        message_text = request.data.get("message")

        if not to_email or not message_text:
            return Response({"error": "Both 'to_email' and 'message' are required."}, status=400)

        try:
            to_user = CustomUser.objects.get(email=to_email)
        except CustomUser.DoesNotExist:
            return Response({"error": "Recipient user not found."}, status=404)

        message = chatMessage.objects.create(
            from_user=from_user,
            to_user=to_user,
            message=message_text
        )

        async_to_sync(notify_chat_message)(message)

        return Response({
            "success": True,
            "message": "Message sent.",
            "data": {
                "from_user": from_user.email,
                "to_user": to_user.email,
                "message": message_text
            }
        })
