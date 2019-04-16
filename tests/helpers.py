from django.urls import reverse
from user.models import User


class TestAPI():

    def set_up(self, testcase):
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

    def get_forbibden(self, testcase, resource, args=None):
        url = reverse(resource, args=args)
        response = testcase.client.get(url, format='json')

        testcase.assertEqual(response.status_code, 403)

    def get_ok(self, testcase, resource, credentials, args=None, results_len=None):
        """User logged in can get list"""

        url = reverse(resource, args=args)
        headers = self.get_headers(
            self.get_access_token(testcase, credentials))

        response = testcase.client.get(
            url,
            format='json',
            **headers
        )

        testcase.assertEqual(response.status_code, 200)

        if results_len:
            testcase.assertEqual(
                len(response.data['results']), results_len)
