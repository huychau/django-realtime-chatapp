from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Profile, Friend


class ProfileSerializer(serializers.ModelSerializer):
    """Profile Serializer"""

    class Meta:
        model = Profile
        fields = (
            'id',
            'url',
            'avatar',
            'phone',
            'bio',
            'birth_date',
            'address',
        )


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""

    # Modify fields
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    profile = ProfileSerializer(read_only=True, many=False)

    class Meta:
        model = User
        fields = (
            'id',
            'url',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_online',
            'profile'
        )

    def __init__(self, *args, **kwargs):
        """Custom to add partial=True to PUT method request to skip blank validations"""

        if kwargs.get('context'):
            request = kwargs['context'].get('request', None)

            if request and getattr(request, 'method', None) == 'PUT':
                kwargs['partial'] = True

        super(UserSerializer, self).__init__(*args, **kwargs)

    def get_fields(self, *args, **kwargs):
        """Custom to add password field in POST method request"""

        fields = super(UserSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)

        # Check request is POST to add password to fields
        if request and getattr(request, 'method', None) == 'POST':
            fields.update({
                'password': serializers.CharField(write_only=True, required=True)
            })
        return fields

    def validate_password(self, value):
        """
        Validate user password
        """
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        """
        Override create method to create user password
        """
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


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
