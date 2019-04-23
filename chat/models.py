from django.db import models
import datetime
from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound
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
            raise NotFound(e)

    def rooms(self, user):
        """
        Get the rooms user created or joined
        """

        return Room.objects.filter(users__id__exact=user.id).order_by('-updated')


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
                    f'You do not add user is not your friend.')

            # Check user is existed
            if new_user in room_users:
                raise ValidationError('You do not add user is existed in this room.')

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
        room_users = room.users.all()

        for user in users:

            # Check user is existed or not
            user = User.objects.get_user(user)

            # Check user does not exist in the room
            if user not in room_users:
                raise ValidationError(
                    'You do not remove user does not exist from this room.')

            room.users.remove(user)

        return room

    def is_member(self, room, user):
        """
        Check is member in the room
        :param room: Room object
        :param user: Request user
        """

        # Check room is instance or integer
        if isinstance(room, int):
            room = Room.objects.get_room(room)

        return user in room.users.all()

    def set_latest_message(self, room, message):
        room = Room.objects.get_room(room.id)
        room.latest_message = message
        room.updated = datetime.datetime.now(tz=timezone.utc)
        room.save()


class MessageManager(models.Manager):
    """
    Message manager
    """

    def messages(self, user, room_id):
        """
        Get last messages
        """

        # Check room is exist or not
        room = Room.objects.get_room(room_id)

        if user not in room.users.all():
            raise ValidationError('You do not get messages from the room you are not joined.')

        return Message.objects.select_related().filter(room=room).order_by('-created')


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
    updated = models.DateTimeField(auto_now_add=True, editable=True)
    latest_message = models.TextField(blank=True)
    photo = models.ImageField(blank=True)

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

    def save(self, *args, **kwargs):
        Room.objects.set_latest_message(self.room, self.message)
        super(Message, self).save(*args, **kwargs)
