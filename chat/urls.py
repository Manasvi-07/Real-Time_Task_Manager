from django.urls import path
from .views import ChatMessageSendAPIView

urlpatterns = [
     path("send/", ChatMessageSendAPIView.as_view(), name="chat-send"),
]