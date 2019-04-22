from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from chatapp import constants
from user.models import User, Friend
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
            'updated',
            'latest_message'
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

        # Check max users in a room
        if len(value) >= constants.ROOM_MAXIMUM_USERS:
            raise ValidationError(
                f'Maximum {constants.ROOM_MAXIMUM_USERS} users in a room.')

        for new_user in value:

            # Check user friendship
            if not Friend.objects.are_friends(user, new_user) and user != new_user:
                raise ValidationError(
                    f'You do not add user is not your friend.')

        return value

    def to_representation(self, instance):
        """Serializer for foreign key"""

        self.fields['users'] = UserSerializer(many=True)
        return super(RoomSerializer, self).to_representation(instance)



class UserInMessageSerializer(serializers.ModelSerializer):
    """Room Serializer"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'full_name'
        )


class MessageSerializer(serializers.ModelSerializer):
    """Message Serializer"""

    user = UserInMessageSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            'id',
            'user',
            'room',
            'message',
            'created',
        )

    def validate_room(self, room):
        """
        Validate room to check user in the room or not
        """

        # Get request user
        user = self.context['request'].user

        # Check user is not in room
        if not Room.objects.is_member(room, user):
            raise ValidationError('You do not send message because you are not member in this room.')
        return room
