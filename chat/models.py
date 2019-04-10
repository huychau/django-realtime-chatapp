from django.db import models
from user.models import User


class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='room_creator')
    users = models.ManyToManyField(User, related_name='room_users', default=user)
    created = models.DateTimeField(auto_now_add=True, editable=False)

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
