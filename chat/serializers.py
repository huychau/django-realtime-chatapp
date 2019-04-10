from rest_framework import serializers
from django.core.exceptions import ValidationError
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

        extra_kwargs = {
            'users': {
                'required': True
            }
        }

    def validate_users(self, value):
        """

        Add creator to the list if not and validate the user list should include at least 2 members
        :param value: User list
        :returns List: User list
        """
        # Get request user
        user = self.context['request'].user

        # Add creator to the members list
        if user not in value:
            value.insert(0, user)

        # In the case only creator
        if len(value) == 1:
            raise ValidationError(['The chat room require at least 2 members.'])

        return value

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
