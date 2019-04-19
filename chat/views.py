from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django.db import IntegrityError
from django.core import serializers
from auth.permissions import (
    IsAdminOrIsSelf,
    IsSelfOrAdminUpdateDeleteOnly,
    IsAdminReadOnly,
)
from .serializers import (
    RoomSerializer,
    MessageSerializer,
)
from .models import Room, Message


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated, IsSelfOrAdminUpdateDeleteOnly)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def list(self, request):
        """
        Get rooms
        """
        queryset = Room.objects.rooms(user=request.user)
        queryset = self.filter_queryset(queryset)
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

        except (ValidationError, IntegrityError) as e:
            return Response({'detail': e.detail[0]}, status.HTTP_400_BAD_REQUEST)

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

        except (ValidationError, IntegrityError) as e:
            return Response({'detail': e.detail[0]}, status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Message viewset
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('message', 'subject')

    def list(self, request):
        """
        Get user messages from a room
        """

        try:

            room_id = request.data.get(
                'room') or request.query_params.get('room')

            queryset = Message.objects.messages(request.user, room_id)
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            serializer = MessageSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        except ValidationError as e:
            return Response({'detail': e.detail[0]}, status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """
        Add `user` param as request user when creating new message
        """

        serializer.save(user=self.request.user)


@login_required
def index(request):
    # Get the last active room
    room = Room.objects.rooms(request.user)[0]
    return redirect('room', room=room.id)

@login_required
def room(request, room):

    # Get all user rooms
    rooms = list(Room.objects.rooms(request.user).values())

    return render(request, 'chat/room.html', {'rooms': rooms})
