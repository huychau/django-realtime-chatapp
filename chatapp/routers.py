from rest_framework import routers
from apps.user.views import UserViewSet

# Routers provide an easy way of automatically determining the URL conf.
api_router = routers.DefaultRouter()
api_router.register('users', UserViewSet, base_name='user')
