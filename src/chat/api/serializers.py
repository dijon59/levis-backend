from rest_framework import serializers
from src.accounts.models import User
from src.chat.models import ChatRoom, ChatMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'contact_number',
            'address',
            'is_customer',
        )


class CustomerSerializer(UserSerializer):
    """
     Serializer dedicated for the creation of customer objects
    """
    class Meta:
        model = User
        fields = (
            'id',
            'contact_number',
            'name',
            'email',
            'is_customer',
        )

        # we remove validators for a specific use case
        validators = []
        extra_kwargs = {
            'email': {'validators': []},
            'contact_number': {'validators': []}
        }

    @staticmethod
    def create_chat_room(customer):
        chat_room_name = f'{customer.id} - {customer.name}'
        ChatRoom.objects.create(user=customer, name=chat_room_name)

    def create(self, validated_data):
        try:
            customer = User.objects.get(email=validated_data.get('email'))
        except User.DoesNotExist:
            customer = super().create(validated_data)
        self.create_chat_room(customer)
        return customer


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = (
            'id',
            'user',
            'name',
            'created_at',
            'status',
            # 'unread_count',
        )

    def to_representation(self, instance: ChatRoom):
        last_message_obj: ChatMessage = instance.messages.first()
        last_message = str(last_message_obj.content) if last_message_obj else None
        representation = super().to_representation(instance)
        representation['user'] = CustomerSerializer(instance.user).data
        representation['last_message'] = last_message
        representation['date_time'] = str(last_message_obj.timestamp) if last_message_obj else str(instance.created_at)
        representation['status'] = instance.status.value
        representation['unread_count'] = instance.messages.filter(is_read=False).count()

        return representation


class ChatMessageSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'room',
            'sender',
            'content',
            'timestamp',
            'is_read',
        )
