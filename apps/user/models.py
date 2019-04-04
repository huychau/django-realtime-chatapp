from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=300, blank=True)
    location = models.CharField(max_length=120, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class UserFriend(models.Model):
    user = models.ForeignKey(
        User, related_name='user', on_delete=models.CASCADE, null=True)
    friend = models.ForeignKey(
        User, related_name='friend', on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
