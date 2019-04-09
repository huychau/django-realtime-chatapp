from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from rest_framework import serializers
from auth.permissions import (
    IsAdminOrIsSelf,
    IsSelfOrAdminUpdateDeleteOnly,
)
from .serializers import (
    RoomSerializer,
    MessageSerializer,
    ParticipantSerializer,
)
from .models import Room, Participant, Message


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsSelfOrAdminUpdateDeleteOnly,
                          IsAuthenticated,)

    def perform_create(self, serializer):
        """
        Add `creator` param as request user when creating new room
        """
        serializer.save(creator=self.request.user)

