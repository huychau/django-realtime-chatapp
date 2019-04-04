
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from auth.permissions import (
    IsAdminOrIsSelf,
    IsSelfOrAdminUpdateDeleteOnly,
    IsAuthenticatedReadOnly,
)
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    PasswordSerializer,
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
    permission_classes = (IsSelfOrAdminUpdateDeleteOnly,
                          IsAuthenticatedReadOnly,)
    ordering = ('-id',)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login by username, password"""

        username = request.data.get('username')
        password = request.data.get('password')

        # Check username, password
        if username is None or password is None:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=status.HTTP_404_NOT_FOUND)

        # Get user token
        token = RefreshToken.for_user(user)

        # Set online status
        user.is_online = True
        user.save()

        # Serializer user to response
        serializer = UserSerializer(user, context={'request': request})
        data = {
            'refresh': str(token),
            'access': str(token.access_token),
            'user': serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def logout(self, request):
        """TODO: Logout default is success"""
        return Response()

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def change_password(self, request, pk=None):
        """Change user password"""

        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid():

            # Validate old password
            if not user.check_password(serializer.data['old_password']):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response({'status': 'Password changed.'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsSelfOrAdminUpdateDeleteOnly,)
    ordering = ('-id',)
