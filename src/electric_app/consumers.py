import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OfferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_request_id = self.scope['url_route']['kwargs']['job_request_id']
        self.group_name = f'job_request_{self.job_request_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        pass

    async def receive(self, text_data):
        # Not used in this case since we're just sending data to the frontend
        pass

    async def send_offer(self, event):
        offer = event['offer']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'offer': offer,
        }))
