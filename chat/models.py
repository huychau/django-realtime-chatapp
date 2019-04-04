from django.db import models


class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)


