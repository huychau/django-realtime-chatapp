from django.urls import reverse
from rest_framework.test import APITestCase
from user.models import User, Profile
from .helpers import TestAPI

test_api = TestAPI()


class UserAPITest(APITestCase):

    def setUp(self):
        test_api.set_up(self)

    def test_string_representation(self):
        user = User.objects.get(pk=1)
        self.assertEqual(str(user), user.username)

        profile = Profile.objects.get(pk=1)
        full_name = f'{profile.first_name} {profile.last_name}'.strip()
        self.assertEqual(str(profile), full_name)


    # REGISTRATION RESOURCES
    #-----------------------

    def test_user_login_empty_credentials(self):
        response = test_api.login(self)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['error'], 'Please provide both username and password')

    def test_user_login_invalid_credentials(self):
        credentials = {
            'username': 'invalid',
            'password': 'invalid'
        }
        response = test_api.login(self, credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Invalid Credentials')

    def test_user_login_ok(self):
        response = test_api.login(
            self, self.normaluser_credentials)
        self.assertEqual(response.status_code, 200)

    def test_user_logout_ok(self):
        url = reverse('logout')
        headers = test_api.get_headers(
            test_api.get_access_token(self, self.normaluser_credentials))
        response = self.client.post(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_create_new_user_empty_fields(self):
        response = test_api.post(self, 'user-list')
        self.assertEqual(response.status_code, 400)

    def test_create_new_user_invalid_data(self):
        data = {
            'username': 'a',
            'password': 'abcd',
            'email': 'invalideemail'
        }

        response = test_api.post(self, 'user-list', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0],
                         'Enter a valid email address.')
        self.assertEqual(
            response.data['username'][0], 'Ensure this field has at least 2 characters.')
        self.assertEqual(
            response.data['password'][0], 'This password is too short. It must contain at least 8 characters.')

    def test_create_new_user_unique_error(self):

        data = {
            'username': self.normaluser_credentials['username'],
            'password': 'abcd@1234',
            'email': 'user@myproject.com'
        }

        response = test_api.post(self, 'user-list', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0],
                        'This field must be unique.')
        self.assertEqual(
            response.data['username'][0], 'user with this username already exists.')

    def test_create_new_user_ok(self):
        data = {
            'username': 'username',
            'password': 'abcd@1234',
            'email': 'username@myproject.com'
        }

        response = test_api.post(self, 'user-list', data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['username'], data['username'])


    # USER RESOURCES
    #---------------

    def test_get_user_list_forbibden(self):
        """User must login to get list user"""

        response = test_api.get(self, 'user-list')
        self.assertEqual(response.status_code, 403)

    def test_get_user_list_ok(self):
        """User must login to get list user"""

        response = test_api.get(self, 'user-list', self.normaluser_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_user_detail_forbibden(self):
        response = test_api.get(self, 'user-detail', None, [self.normaluser.id])

        self.assertEqual(response.status_code, 403)

    def test_get_user_detail_ok(self):
        response = test_api.get(self, 'user-detail', self.normaluser_credentials, [self.normaluser.id])

        self.assertEqual(response.status_code, 200)

    def test_update_user_info_forbibden(self):
        """
        Normal user can not update other use info
        """

        data = {
            'email': 'newemail@myproject.com'
        }
        response = test_api.put(
            self, 'user-detail', data, self.normaluser_credentials, args=[self.superuser.id])

        self.assertEqual(response.status_code, 403)

    def test_update_user_info_ok(self):
        data = {
            'email': 'newemail@myproject.com'
        }

        response = test_api.put(
            self, 'user-detail', data, self.normaluser_credentials, args=[self.normaluser.id])

        self.assertEqual(response.status_code, 200)

    def test_user_change_password_empty_field(self):
        response = test_api.put(
            self, 'user-change-password', {}, self.normaluser_credentials, args=[self.normaluser.id])

        self.assertEqual(response.status_code, 400)

    def test_user_change_password_invalid_old_password(self):
        data = {
            'old_password': 'wrong',
            'new_password': 'newpassword'
        }

        response = test_api.put(
            self, 'user-change-password', data, self.normaluser_credentials, args=[self.normaluser.id])

        self.assertEqual(response.status_code, 400)

    def test_user_change_password_ok(self):

        data = {
            'old_password': self.normaluser_credentials['password'],
            'new_password': 'newpassword'
        }

        response = test_api.put(
            self, 'user-change-password', data, self.normaluser_credentials, args=[self.normaluser.id])

        self.assertEqual(response.status_code, 200)


    # PROFILE RESOURCES
    #------------------
    def test_get_user_profile(self):
        response = test_api.get(
            self, 'profile-me', self.normaluser_credentials)
        self.assertEqual(response.status_code, 200)


    # FRIEND RESOURCES
    #------------------

    def test_get_friend_list(self):
        data = {
            'user_id': self.superuser.id,
            'message': 'hi!'
        }

        # Add new friend
        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 201)

        response = test_api.get(
            self, 'friend-list', self.normaluser_credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_add_new_friend_empty_id(self):
        response = test_api.post(
            self, 'friend-list', {}, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)

    def test_add_new_friend_user_not_found(self):
        data = {'user_id': 100}

        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 404)

    def test_add_new_friend_can_not_add_themselves(self):

        data = {'user_id': self.normaluser.id}

        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)

    def test_add_new_friend_already_exist(self):
        data = {
            'user_id': self.superuser.id,
            'message': 'hi!'
        }

       # Add new friend
        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 201)

        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)


    def test_add_new_friend_ok(self):
        data = {
            'user_id': self.superuser.id,
            'message': 'hi!'
        }
        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 201)

    def test_delete_friend_empty_user_id(self):
        response = test_api.delete(
            self, 'friend-list', None, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)

    def test_delete_friend_not_existed(self):
        data = {'user_id': self.superuser.id}

        response = test_api.delete(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)

    def test_delete_friend_ok(self):
        data = {
            'user_id': self.superuser.id,
            'message': 'hi!'
        }

        # Add new friend
        response = test_api.post(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 201)

        data = {'user_id': self.superuser.id}

        response = test_api.delete(
            self, 'friend-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 204)
