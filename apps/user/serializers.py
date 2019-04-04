from django.contrib.auth.models import User, Group
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""
    # url = serializers.HyperlinkedRelatedField(view_name='api:user-detail', source='user', read_only=True)

    # Modify fields
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'id',
            # 'url',
            'username',
            'email',
            'first_name',
            'last_name',
        )
