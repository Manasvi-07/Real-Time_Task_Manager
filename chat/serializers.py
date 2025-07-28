from rest_framework import serializers
from .models import chatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    from_username = serializers.CharField(source='sender.email', read_only=True)
    from_user = serializers.IntegerField(source='sender.id', read_only=True)
    from_role = serializers.CharField(source='sender.role', read_only=True)
    to_username = serializers.CharField(source='receiver.email', read_only=True)
    to_user = serializers.IntegerField(source='receiver.id', read_only=True)

    class Meta:
        model = chatMessage
        fields = ['id', 'message', 'from_user', 'from_username', 'from_role', 'to_user', 'to_username']
