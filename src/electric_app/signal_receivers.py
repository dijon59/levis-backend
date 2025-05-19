from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from src.chat.models import ChatMessage


def notify_chat_room_update_consumer(chat_message: ChatMessage):
    channel_layer = get_channel_layer()
    chat_room = chat_message.room
    chat_room.refresh_from_db()
    async_to_sync(channel_layer.group_send)(
        'chat_room_update_controller',
        {
            'type': 'chat_room_update',
            "id": chat_room.id,
            "user": {
                'id': chat_room.user.id,
                'contact_number': str(chat_room.user.contact_number),
                'name': chat_room.user.name,
                'email': chat_room.user.email,
            },
            'created_at': str(chat_message.timestamp),
            "last_message": '' if chat_message.image else chat_message.content,
            "status": chat_room.status.value,
            "unread_count": chat_room.messages.filter(is_read=False).count(),
        }
    )


@receiver(post_save, sender=ChatMessage)
def update_chat_room(sender, instance, created, **kwargs):
    if created:
        notify_chat_room_update_consumer(instance)
