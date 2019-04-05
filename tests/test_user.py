from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User, Profile
from .helpers import TestAPI

test_api = TestAPI()


class UserAPITest(APITestCase):

    def setUp(self):
        test_api.set_up(self)

    def test_get_user_list_forbibden(self):
        """User must login to get list user"""

        test_api.get_forbibden(self, 'user-list')

    def test_get_user_list_ok(self):
        """User must login to get list user"""

        test_api.get_ok(self, 'user-list', self.normaluser_credentials, None, 2)

    def test_get_user_detail_forbibden(self):
        test_api.get_forbibden(self, 'user-detail', [self.normaluser.id])

    def test_get_user_detail_ok(self):
        test_api.get_ok(self, 'user-detail',
                               self.normaluser_credentials, [self.normaluser.id])
