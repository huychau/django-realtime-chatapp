from rest_framework import serializers
from user.serializers import UserSerializer
from .models import Room, Message


class RoomSerializer(serializers.ModelSerializer):
    """Room Serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Room
        fields = (
            'id',
            'name',
            'label',
            'user',
            'users',
            'url',
        )

    def to_representation(self, instance):
        """Serializer for foreign key"""

        self.fields['users'] = UserSerializer(many=True)
        return super(RoomSerializer, self).to_representation(instance)


class MessageSerializer(serializers.ModelSerializer):
    """Message Serializer"""

    class Meta:
        model = Message
        fields = (
            'id',
        )
