from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, UserManager as AbstractUserManager
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save
from chatapp import settings


class UserManager(AbstractUserManager):
    """
    User manager
    """

    def get_user(self, pk):
        """
        Get user instance and raise error if user does not exist
        """
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist as e:
            raise NotFound(e)


class FriendshipManager(models.Manager):
    """
    Friendship manager
    """

    def friends(self, user):
        """
        Return a list of all friends
        """

        friends = Friend.objects.select_related(
            'from_user', 'to_user').filter(Q(from_user=user) | Q(to_user=user)).all()


        # Check to get only user friend object
        results = []

        for friend in friends:

            friend_obj = friend.from_user == user and friend.to_user or friend.from_user

            results.append(friend_obj)

        return results

    def add_friend(self, from_user, to_user, message=None):
        """
        Create a friendship request
        """

        if from_user == to_user:
            raise ValidationError('Users cannot be friends with themselves.')

        if self.are_friends(from_user, to_user):
            raise ValidationError('Users are already friends.')

        request, created = Friend.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
        )

        if message:
            request.message = message or ''
            request.save()

        return request

    def remove_friend(self, from_user, to_user):
        """
        Destroy a friendship relationship
        """

        qs = Friend.objects.filter(
            Q(to_user=to_user, from_user=from_user) |
            Q(to_user=from_user, from_user=to_user)
        ).distinct().all()

        if qs:
            qs.delete()
            return True
        else:
            raise ValidationError('Friendship does not exist.')


    def are_friends(self, user_1, user_2):
        """
        Check users are friends
        """
        friends = Friend.objects.filter(Q(from_user=user_1, to_user=user_2) | Q(from_user=user_2, to_user=user_1))

        return len(friends) > 0


class User(AbstractUser):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    username = models.CharField(
        _('username'), unique=True, max_length=50, validators=[MinLengthValidator(2),])
    password = models.CharField(_('password'), max_length=128)
    email = models.EmailField(_('email address'), unique=True)
    is_online = models.BooleanField(default=False)

    objects = UserManager()

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.OneToOneField(settings.base.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()

    class Meta:
        ordering = ('-id',)


class Friend(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_user = models.ForeignKey(
        settings.base.AUTH_USER_MODEL, related_name='creator', on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        settings.base.AUTH_USER_MODEL, related_name='friends', on_delete=models.CASCADE)
    message = models.CharField(max_length=100, blank=True)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        unique_together = ('from_user', 'to_user')
        ordering = ('-id',)


# Auto create user profile when user is created
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)
        return profile

post_save.connect(create_user_profile, sender=User)
