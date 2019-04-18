from django.urls import reverse
from rest_framework.test import APITestCase
from user.models import User


class HelperAPITestCase(APITestCase):

    def setUp(self):
        """
        Set up new normal and super users
        """

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

    def login(self, credentials=None):
        url = reverse('login')
        return self.client.post(
            url,
            credentials,
            format='json'
        )

    def get_access_token(self, credentials=None):

        if credentials:
            response = self.login(credentials)

            self.assertEqual(response.status_code, 200)

            return 'Bearer {}'.format(response.data['access'])

    def get_headers(self, access_token):
        return {
            'HTTP_AUTHORIZATION': access_token
        }


    def get(self, resource, credentials=None, args=None, data=None):
        """
        Helper for get API method
        :param testcase: APITestCase
        :param resource: API resource (URL string)
        :param credentials: User credentials
        :param args: Resource detail arguments
        returns: Response
        """

        url = reverse(resource, args=args)

        headers = {}
        if credentials:
            headers = self.get_headers(
                self.get_access_token(credentials))

        return self.client.get(
            url,
            data=data,
            format='json',
            **headers
        )

    def post(self, resource, data=None, credentials=None, args=None):
        """
        Helper for post API method
        :param testcase: APITestCase
        :param resource: API resource (URL string)
        :param credentials: User credentials
        :param args: Resource detail arguments
        returns: Response
        """

        url = reverse(resource, args=args)

        headers = {}
        if credentials:
            headers = self.get_headers(
                self.get_access_token(credentials))

        return self.client.post(
            url,
            data,
            format='json',
            **headers
        )

    def put(self, resource, data=None, credentials=None, args=None):
        """
        Helper for put API method
        :param testcase: APITestCase
        :param resource: API resource (URL string)
        :param credentials: User credentials
        :param args: Resource detail arguments
        returns: Response
        """

        url = reverse(resource, args=args)

        headers = {}
        if credentials:
            headers = self.get_headers(
                self.get_access_token(credentials))

        return self.client.put(
            url,
            data,
            format='json',
            **headers
        )

    def delete(self, resource, data=None, credentials=None, args=None):
        """
        Helper for delete API method
        :param testcase: APITestCase
        :param resource: API resource (URL string)
        :param credentials: User credentials
        :param args: Resource detail arguments
        returns: Response
        """

        url = reverse(resource, args=args)

        headers = {}
        if credentials:
            headers = self.get_headers(
                self.get_access_token(credentials))

        return self.client.delete(
            url,
            data,
            format='json',
            **headers
        )
