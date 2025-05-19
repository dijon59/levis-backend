from django.urls import path
from src.chat.consumer import ChatConsumer, ChatRoomUpdateControllerConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:chat_room_id>/', ChatConsumer.as_asgi()),
    path('ws/chat_room_update/', ChatRoomUpdateControllerConsumer.as_asgi()),
]
