from django.db import models
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from user.models import User, Friend
from chatapp import constants


class RoomManager(models.Manager):
    """
    Room manager
    """

    def add_users(self, request_user, room_id, users):
        """
        Add new users to existed room
        :param room_id: Room ID
        :param users: List of user ID added to room
        """

        if not isinstance(users, (list,)) or not len(users):
            raise ValidationError('New users must a list and not empty.')

        room = Room.objects.get(pk=room_id)

        for user in users:

            # Check user friendship
            if not Friend.objects.are_friends(request_user, user):
                raise ValidationError('You can not add user is not friendship.')

            # Check max users in a room
            if len(room.users.all()) >= constants.ROOM_MAXIMUM_USERS:
                raise ValidationError(
                    f'Maximum {constants.ROOM_MAXIMUM_USERS} users in a room.')

            # Check user is existed or not
            get_object_or_404(User, pk=user)
            room.users.add(user)

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
            get_object_or_404(User, pk=user)
            room.users.remove(user)

        return room


class MessageManager(models.Manager):
    """
    Message manager
    """

    def last_messages(self, room):
        """
        Get last messages
        """
        return Message.objects.filter(room=room).order_by('-id')[:constants.MESSAGE_MAXIMUM]


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

    objects = MessageManager

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'Message from {self.user}'
