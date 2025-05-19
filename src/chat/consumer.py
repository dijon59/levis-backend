import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from src.chat.api.serializers import ChatRoomSerializer
from src.chat.models import ChatMessage, ChatRoom
from src.accounts.models import User
from django.core.files.base import ContentFile
import base64
from datetime import datetime


class ChatRoomUpdateControllerConsumer(AsyncWebsocketConsumer):
    """
    This class controls the notification send to client:
    - update messages count
    - update chat room list
    - update message previous
    """

    room_group_name = 'chat_room_update_controller'

    async def connect(self):

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'load_chat_room',
                'chat_rooms': await self.fetch_chatrooms(),
            }
        )
    @database_sync_to_async
    def fetch_chatrooms(self) -> list:
        return ChatRoomSerializer(ChatRoom.objects.filter(messages__is_read=False).distinct(), many=True).data


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # update chat room last_message and unread_count
    async def chat_room_update(self, event):
        id = event['id']
        user = event['user']
        last_message = event['last_message']
        unread_count = event['unread_count']
        created_at = event['created_at']
        status = event['status']

        await self.send(text_data=json.dumps({
            'type': 'room_update',
            'id': id,
            'user': user,
            'created_at': created_at,
            'last_message': last_message,
            'unread_count': unread_count,
            'status': status,
        }))

    async def load_chat_room(self, event):
        chat_rooms = event['chat_rooms']

        await self.send(text_data=json.dumps({
            'type': 'load_rooms',
            'chat_rooms': chat_rooms,
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Controls chat between client and server
    """

    async def connect(self):
        self.chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
        self.room_group_name = f'chat_{self.chat_room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        self.room = await self.get_room()
        self.room_id = self.room.id

        messages = await self.get_messages()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'fetch_messages',
                'messages': messages,
            }
        )

    @database_sync_to_async
    def get_messages(self) -> list:
        messages = ChatMessage.objects.filter(
            room_id=self.room_id
        ).order_by('-timestamp')

        return [
            {'id': message.id,
             'message': message.content,
             'is_customer': message.sender.is_customer,
             'user_id': message.sender.id,
             'timestamp': str(message.timestamp),
             'image_url': message.image.url if message.image else None,
             }
            for message in messages
        ]

    @database_sync_to_async
    def get_room(self):
        return ChatRoom.objects.get(id=self.chat_room_id)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']
        chat_room_id = data['chat_room_id']
        is_customer = data['is_customer']
        is_sent = data['is_sent']
        image_base64 = data['image_url']

        image_data = None
        if image_base64:
            image_data = await self.get_converted_image(image_base64)

        await self.handle_chat_message(
            chat_room_id,
            sender_id,
            message,
            is_customer,
            is_sent,
            image_data,
            image_base64
        )

    async def handle_chat_message(
            self,
            chat_room_id,
            sender_id,
            message,
            is_customer,
            is_sent,
            image_data=None,
            image_base64=None):

        chat: ChatMessage = await self.save_message(sender_id, message, image_data)

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'created_at': str(chat.timestamp),
                'is_customer': is_customer,
                'is_sent': is_sent,
                'image_url': image_base64,
            }
        )

    async def get_converted_image(self, base64_image):
        # Decode the base64 image
        format, imgstr = base64_image.split(';base64,')  # Split the metadata from the base64 content
        ext = format.split('/')[-1]  # Extract the file extension (e.g., 'png', 'jpeg')
        image_name = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"  # Create a unique file name

        # Convert base64 to binary
        image_data = ContentFile(base64.b64decode(imgstr), name=image_name)

        return image_data

    @database_sync_to_async
    def update_chat_rooms(self, sender_id, chat_room_id, last_message_content):
        chat_room = ChatRoom.objects.get(id=chat_room_id)
        chat_room.last_message = last_message_content
        chat_room.save()

    async def fetch_messages(self, event):
        messages = event['messages']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'messages': messages
        }))

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        created_at = event['created_at']
        is_customer = event['is_customer']
        is_sent = event['is_sent']
        image_url = event['image_url']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'created_at': created_at,
            'is_customer': is_customer,
            'is_sent': is_sent,
            'image_url': image_url,
        }))

    @database_sync_to_async
    def save_message(self, user_id, message, image_data=None):
        user: User = User.objects.get(id=user_id)
        is_read = False
        if not user.is_customer:
            # if the message sender is admin, we automatically set is_read=True
            is_read = True

        chat: ChatMessage = ChatMessage.objects.create(
            room=self.room,
            sender=user,
            content=message,
            image=image_data,
            is_read=is_read
        )

        return chat
