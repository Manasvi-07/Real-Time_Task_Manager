import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        print(" WebSocket Connected User : ", user)

        if user.is_authenticated:
            self.group_name = f"user_{user.id}"
            print("Group name : ",self.group_name)
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            print("User not authenticated. Closing connection.")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def task_update(self, event):
        print("SENDING TO WEBSOCKET:", event)
        await self.send(text_data=json.dumps(event['data']))