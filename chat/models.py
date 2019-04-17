from django.db import models
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from user.models import User, Friend
from chatapp import constants


class RoomManager(models.Manager):
    """
    Room manager
    """

    def get_room(self, pk):
        """
        Get room instance and raise error if room does not exist
        """

        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist as e:
            raise ValidationError(e)

    def rooms(self, user):
        """
        Get the rooms user created or joined
        """

        return Room.objects.filter(users__id__exact=user.id)


    def add_users(self, request_user, room_id, users):
        """
        Add new users to existed room
        :param room_id: Room ID
        :param users: List of user ID added to room
        """

        if not isinstance(users, (list,)) or not len(users):
            raise ValidationError('New users must a list and not empty.')

        room = Room.objects.get_room(room_id)

        room_users = room.users.all()

        for new_user in users:

            # Check max users in a room
            if len(room_users) >= constants.ROOM_MAXIMUM_USERS:
                raise ValidationError(
                    f'Maximum {constants.ROOM_MAXIMUM_USERS} users in a room.')

            new_user = User.objects.get_user(new_user)

            # Check user is not friendship
            if not Friend.objects.are_friends(request_user, new_user) and request_user != new_user:
                raise ValidationError(
                    f'You can not add user {new_user} because this user is not your friend.')

            # Check user is existed
            if new_user in room_users:
                raise ValidationError('You can not add user is existed in this room.')

            room.users.add(new_user)

        return room

    def remove_users(self, room_id, users):
        """
        Remove users from existed room
        :param room_id: Room ID
        :param users: List of user ID removed from room
        """
        if not isinstance(users, (list,)) or not len(users):
            raise ValidationError('Users must a list and not empty.')

        room = Room.objects.get(pk=room_id)

        for user in users:

            # Check user is existed or not
            user = User.objects.get_user(user)
            room.users.remove(user)

        return room

    def get_users(self, room):
        """
        Get users in a room
        :param room: Room object
        """
        return room.users.all()

    def is_member(self, room, user):
        """
        Check is member in the room
        :param room: Room object
        :param user: Request user
        """

        # Check room is
        if isinstance(room, int):
            room = Room.objects.filter(pk=room)

            if not len(room):
                raise ValidationError('Room not found.')

        return user in room[0].users.all()


class MessageManager(models.Manager):
    """
    Message manager
    """

    def last_messages(self, room_id):
        """
        Get last messages
        """

        # Check room is exist or not
        if not Room.objects.filter(pk=room_id).exists():
            raise ValidationError('Can not found this room.')

        return Message.objects.filter(room=room_id).order_by('-created')[:constants.MESSAGE_MAXIMUM][::-1]


class Room(models.Model):
    """
    Room model
    """

    name = models.TextField()
    label = models.SlugField(unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='room_creator')
    users = models.ManyToManyField(User, related_name='room_users', default=user)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objects = RoomManager()

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Message(models.Model):
    """
    Message model
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='message_sender')
    subject = models.CharField(max_length=1000, blank=True)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objects = MessageManager()

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'Message from {self.user}'
