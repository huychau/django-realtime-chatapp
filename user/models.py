from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from chatapp import settings


class User(AbstractUser):
    username = models.CharField(_('username'), unique=True, max_length=80)
    email = models.EmailField(_('email address'), unique=True)
    is_online = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(settings.base.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    address = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ('-id',)
