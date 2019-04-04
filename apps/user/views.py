from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from apps.auth.permissions import (
    IsAdminListOnly,
    IsSelfOrAdminUpdateDeleteOnly
)
from .serializers import (
    UserSerializer,
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Permissons:
        - Allow anonymous can create, view user detail
        - Allow owner or admin can edit profile, change password, delete user
        - Allow anonymous can login
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrAdminUpdateDeleteOnly,)
    ordering = ('-id',)
