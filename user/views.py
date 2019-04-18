
from django.contrib.auth import authenticate, get_user_model, logout as auth_logout
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, list_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import RefreshToken
from auth.permissions import (
    IsAdminOrIsSelf,
    IsSelfOrAdminUpdateDeleteOnly,
    IsAuthenticatedReadOnly,
)
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    FriendSerializer,
    PasswordSerializer,
)
from .models import User, Profile, Friend


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
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    ordering = ('-id',)

    @action(detail=True, methods=['put'],
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
            return Response({'detail': 'Password changed.'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsSelfOrAdminUpdateDeleteOnly,)
    ordering = ('-id',)

    @list_route(methods=['GET'],)
    def me(self, request, *args, **kwargs):
        """
        Get current user profile
        """
        self.kwargs.update(pk=request.user.id)
        return self.retrieve(request, *args, **kwargs)


class FriendViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows friends to be viewed or edited.
    """
    queryset = ''
    serializer_class = FriendSerializer
    permission_classes = (IsAuthenticated, IsSelfOrAdminUpdateDeleteOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    ordering = ('-id',)

    def list(self, request):
        """
        Get friends
        """
        queryset = Friend.objects.friends(request.user)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = UserSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        """
        Creates a friend request
        :param user_id: Friend ID
        :param message: Add friend message
        returns: Friendship object
        """

        user_id = request.data.get('user_id', None)

        if not user_id:
            return Response(
                {'user_id': ['User ID is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            friend_obj = Friend.objects.add_friend(
                request.user, #The sender
                User.objects.get_user(user_id),  # The recipient
                message=request.data.get('message', '')
            )

            return Response(
                FriendSerializer(friend_obj, context={
                                 'request': request}).data,
                status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({'detail': e.detail[0]}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=False)
    def delete(self, request, pk=None):
        """
        Creates a delete friend request
        :param user_id: Friend ID
        returns: Friendship object
        """

        user_id = request.data.get('user_id', None)

        if not user_id:
            return Response(
                {'user_id': ['User ID is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            success = Friend.objects.remove_friend(request.user, user_id)
            if success:
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
        except ValidationError as e:
            return Response({'detail': e.detail[0]}, status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def login(request):
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
                        status=status.HTTP_401_UNAUTHORIZED)

    # Get user token
    token = RefreshToken.for_user(user)

    # Set online status
    user.is_online = True
    user.save()

    # Get user profile
    profile = Profile.objects.get(user=user)

    # Serializer user to response
    serializer = ProfileSerializer(profile, context={'request': request})

    data = {
        'refresh': str(token),
        'access': str(token.access_token),
        'profile': serializer.data
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def logout(request):
    """TODO: Logout default is success"""

    return Response()
