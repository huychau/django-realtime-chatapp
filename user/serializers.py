from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Profile


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

    user = UserSerializer()

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
