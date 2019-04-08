from rest_framework import serializers
from user.serializers import UserSerializer
from .models import Room, Participant, Message


class RoomSerializer(serializers.ModelSerializer):
    """Room Serializer"""

    creator = UserSerializer(read_only=True)

    class Meta:
        model = Room
        fields = (
            'id',
            'name',
            'label',
            'creator'
        )


class ParticipantSerializer(serializers.ModelSerializer):
    """Participant Serializer"""

    creator = UserSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = (
            'id',
        )


class MessageSerializer(serializers.ModelSerializer):
    """Message Serializer"""

    creator = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            'id',
        )
