from django.urls import reverse
from user.models import User


class TestAPI():

    def set_up(self, testcase):
        """
        Set up new normal and super users
        """

        testcase.superuser_credentials = {
            'username': 'admin',
            'password': 'password'
        }

        testcase.normaluser_credentials = {
            'username': 'user',
            'password': 'password'
        }

        # Create superuser
        testcase.superuser = User.objects.create_superuser(
            testcase.superuser_credentials['username'],
            'admin@myproject.com',
            testcase.superuser_credentials['password'],
        )

        # Create normal user
        testcase.normaluser = User.objects.create_user(
            testcase.normaluser_credentials['username'],
            'user@myproject.com',
            testcase.normaluser_credentials['password']
        )

    def login(self, testcase, credentials=None):
        url = reverse('login')
        return testcase.client.post(
            url,
            credentials,
            format='json'
        )

    def get_access_token(self, testcase, credentials=None):

        if credentials:
            response = self.login(testcase, credentials)

            testcase.assertEqual(response.status_code, 200)

            return 'Bearer {}'.format(response.data['access'])

    def get_headers(self, access_token):
        return {
            'HTTP_AUTHORIZATION': access_token
        }


    def get(self, testcase, resource, credentials=None, args=None, results_len=None):
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
                self.get_access_token(testcase, credentials))

        return testcase.client.get(
            url,
            format='json',
            **headers
        )

    def post(self, testcase, resource, data=None, credentials=None, args=None):
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
                self.get_access_token(testcase, credentials))

        return testcase.client.post(
            url,
            data,
            format='json',
            **headers
        )

    def put(self, testcase, resource, data=None, credentials=None, args=None):
        """
        Helper for pust API method
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
                self.get_access_token(testcase, credentials))

        return testcase.client.put(
            url,
            data,
            format='json',
            **headers
        )

