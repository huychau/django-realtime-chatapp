from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User, Group


class UserAPITest(APITestCase):

    def setUp(self):

        self.superuser_credentials = {
            'username': 'admin',
            'password': 'password'
        }

        self.normaluser_credentials = {
            'username': 'user',
            'password': 'password'
        }

        # Create superuser
        self.superuser = User.objects.create_superuser(
            self.superuser_credentials['username'],
            'admin@myproject.com',
            self.superuser_credentials['password'],
        )

        # Create normal user
        self.normaluser = User.objects.create_user(
            self.normaluser_credentials['username'],
            'user@myproject.com',
            self.normaluser_credentials['password']
        )

    def test_get_user_list_forbidden(self):
        """Only super user can get list user"""

        url = reverse('api:user-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 403)

