from rest_framework import routers
from user.views import UserViewSet, ProfileViewSet

# Routers provide an easy way of automatically determining the URL conf.
api_router = routers.DefaultRouter()
api_router.register('users', UserViewSet, base_name='user')
api_router.register('profiles', ProfileViewSet, base_name='profile')
