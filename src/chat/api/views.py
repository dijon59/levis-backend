from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from src.chat.enums import ChatRoomStatus
from .serializers import ChatRoomSerializer, ChatMessageSerializer, CustomerSerializer
from src.chat.models import ChatMessage, ChatRoom
from rest_framework.decorators import action
from rest_framework.response import Response


class ChatMessageViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ChatMessageSerializer
    pagination_class = None

    def get_queryset(self):
        chat_room_id = self.request.query_params.get('chat_room_id')
        messages = ChatMessage.objects.filter(room_id=chat_room_id)
        return messages


class ChatRoomViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ChatRoomSerializer
    pagination_class = None

    def get_queryset(self):
        query_param = self.request.query_params.get('param')

        if query_param == 'completed':
            return ChatRoom.objects.filter(status=ChatRoomStatus.COMPLETED).order_by('-created_at')
        if query_param == 'in progress':
            return ChatRoom.objects.filter(status=ChatRoomStatus.IN_PROGRESS).order_by('-created_at')
        if query_param == 'pending':
            return ChatRoom.objects.filter(status=ChatRoomStatus.PENDING).order_by('-created_at')
        return ChatRoom.objects.filter(status=ChatRoomStatus.ACTIVE).order_by('-created_at')

    @action(
            detail=True,
            methods=['PUT'],
            url_name='mark_as_completed',
            url_path='mark_as_completed',
    )
    def mark_as_completed(self, request, pk=None):
        c_room = get_object_or_404(ChatRoom, pk=pk)
        c_room.status = ChatRoomStatus.COMPLETED
        c_room.save()
        return Response({'message': 'Marked as completed'}, status=status.HTTP_200_OK)

    @action(
            detail=True,
            methods=['PUT'],
            url_name='mark_as_in_progress',
            url_path='mark_as_in_progress',
    )
    def marks_as_in_progress(self, request, pk=None):
        c_room = get_object_or_404(ChatRoom, pk=pk)
        c_room.status = ChatRoomStatus.IN_PROGRESS
        c_room.save()
        return Response({'message': 'Marked as in progress'}, status=status.HTTP_200_OK)

    @action(
            detail=True,
            methods=['PUT'],
            url_name='mark_as_pending',
            url_path='mark_as_pending',
    )
    def marks_as_pending(self, request, pk=None):
        c_room = get_object_or_404(ChatRoom, pk=pk)
        c_room.status = ChatRoomStatus.PENDING
        c_room.save()
        return Response({'message': 'Marked as pending'}, status=status.HTTP_200_OK)
    
    @action(
            detail=True,
            methods=['PUT'],
            url_name='mark_as_read',
            url_path='mark_as_read',
    )
    def marks_as_read(self, request, pk=None):
        c_room = get_object_or_404(ChatRoom, pk=pk)
        unread_messages: ChatMessage = c_room.messages.filter(is_read=False)
        for message in unread_messages:
            message.is_read = True
        c_room.messages.bulk_update(unread_messages, ['is_read'])
        return Response({'message': 'Marked as read'}, status=status.HTTP_200_OK)


class CustomerCreateViewset(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = CustomerSerializer

    def get_chat_room_id(self, data):
        chatRoom = ChatRoom.objects.filter(user__email=data['email'], status=ChatRoomStatus.ACTIVE).first()
        serializedData =  ChatRoomSerializer(chatRoom).data
        return serializedData['id']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['chat_room_id'] = self.get_chat_room_id(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
