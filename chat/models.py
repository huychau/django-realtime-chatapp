from django.db import models
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from user.models import User
from chatapp import constants


class RoomManager(models.Manager):
    """
    Room manager
    """

    def add_users(self, room_id, users):
        """
        Add new users to existed room
        :param room_id: Room ID
        :param users: List of user ID added to room
        """

        if not isinstance(users, (list,)) or not len(users):
            raise ValidationError('New users must a list and not empty.')

        room = Room.objects.get(pk=room_id)

        for user in users:

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


class Room(models.Model):
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
    room = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='message_sender')
    subject = models.CharField(max_length=1000, blank=True)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return 'Message from {self.user}'
