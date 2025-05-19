from django.db import models
from src.accounts.models import User
from enumfields import EnumField
from .enums import ChatMessageType, ChatRoomStatus


class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = EnumField(ChatRoomStatus, default=ChatRoomStatus.ACTIVE, max_length=100)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    type = EnumField(ChatMessageType, default=ChatMessageType.TEXT, max_length=13)
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
