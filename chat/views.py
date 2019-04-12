from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
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
            return Response({'error': err}, status.HTTP_400_BAD_REQUEST)

        except Room.DoesNotExist as e:
            return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)

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
    permission_classes = (IsAuthenticated, IsAdminReadOnly)

    def perform_create(self, serializer):
        """
        Add `user` param as request user when creating new message
        """

        serializer.save(user=self.request.user)


def index(request):
    return render(request, 'chat/index.html', {})

@login_required
def room(request, room):
    return render(request, 'chat/room.html', {})
