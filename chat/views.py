from django.utils.safestring import mark_safe
import json
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from rest_framework import serializers
from auth.permissions import (
    IsAdminOrIsSelf,
    IsSelfOrAdminUpdateDeleteOnly,
    IsAdmin,
)
from .serializers import (
    RoomSerializer,
    MessageSerializer,
)
from .models import Room, Message


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsSelfOrAdminUpdateDeleteOnly, IsAuthenticated,)

    def list(self, request):
        """
        Get rooms
        """
        queryset = Room.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = RoomSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        """
        Add `user` param as request user when creating new room
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_users(self, request, pk=None):
        """
        Creator can add more users to the room
        """

        try:
            users = request.data.get('users', [])

            room = Room.objects.add_users(request.user, pk, users)
            serializer = RoomSerializer(room, context={'request': request})
            return Response(serializer.data)

        except (ValidationError, IntegrityError) as err:
            return Response({'users': err}, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_users(self, request, pk=None):
        """
        Creator can remove users from the room
        """

        try:
            users = request.data.get('users', [])

            room = Room.objects.remove_users(pk, users)
            serializer = RoomSerializer(room, context={'request': request})
            return Response(serializer.data)

        except (ValidationError, IntegrityError) as err:
            return Response({'users': err}, status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Message viewset
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAdmin, IsAuthenticated,)


# For test websocket
def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })
