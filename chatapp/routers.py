from rest_framework import routers
from django.urls import path
from user.views import UserViewSet, ProfileViewSet, FriendViewSet, login, logout
from chat.views import RoomViewSet, MessageViewSet

# Routers provide an easy way of automatically determining the URL conf.
api_router = routers.DefaultRouter()
api_router.register('users', UserViewSet, base_name='user')
api_router.register('profiles', ProfileViewSet, base_name='profile')
api_router.register('friends', FriendViewSet, base_name='friend')
api_router.register('rooms', RoomViewSet, base_name='room')
api_router.register('messages', MessageViewSet, base_name='message')

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]

urlpatterns += api_router.urls
