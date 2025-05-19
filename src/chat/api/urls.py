from src.chat.api import views
from src.accounts.api.urls import api


apis = [
    api(r'chat-rooms', views.ChatRoomViewset, name='chat-room'),
    api(r'chat-messages', views.ChatMessageViewset, name='chat-messages'),
    api(r'register-customer', views.CustomerCreateViewset, name='register-customer')
]
