
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from auth.permissions import (
    IsAdminOrIsSelf,
    IsSelfOrAdminUpdateDeleteOnly,
)
from .serializers import (
    UserSerializer,
    ProfileSerializer,
)
from .models import User, Profile


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


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsSelfOrAdminUpdateDeleteOnly,)
    ordering = ('-id',)
