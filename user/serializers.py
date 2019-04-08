from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Profile, Friend


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""

    url = serializers.HyperlinkedRelatedField(view_name='api:user-detail', source='user', read_only=True)

    # Modify fields
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'id',
            'url',
            'username',
            'email',
            'is_online'
        )


class ProfileSerializer(serializers.ModelSerializer):
    """Profile Serializer"""

    user = UserSerializer(read_only=True)

    url = serializers.HyperlinkedRelatedField(
        view_name='api:profile-detail', source='profile', read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id',
            'url',
            'user',
            'first_name',
            'last_name',
            'phone',
            'bio',
            'birth_date',
            'address',
        )


class FriendSerializer(serializers.ModelSerializer):
    """Friend Serializer"""

    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = (
            'id',
            'from_user',
            'to_user',
            'message',
            'created'
        )

class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
