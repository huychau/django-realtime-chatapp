from django.db import models
from user.models import User


class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='room_creator')
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='message_sender')
    subject = models.CharField(max_length=1000, blank=True)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return 'Message from {self.sender} to {self.}'


class Participant(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='participant_user')
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='participant_group')

    class Meta:
        ordering = ('-id',)
