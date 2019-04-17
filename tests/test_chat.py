from rest_framework.test import APITestCase
from chat.models import Room, Message
from user.models import Friend, User
from .helpers import TestAPI

test_api = TestAPI()


class ChatAPITest(APITestCase):
    def setUp(self):
        test_api.set_up(self)

        self.user2 = User.objects.create_user(
            'user2', 'user2@project.com', 'password')
        self.user3 = User.objects.create_user(
            'user3', 'user3@project.com', 'password')

        self.room1 = Room.objects.create(
            user=self.normaluser,
            label='test-room-1',
            name='Test Room 1'
        )

        self.room1.users.add(self.normaluser, self.superuser)

        self.message = Message.objects.create(
            room=self.room1,
            user=self.normaluser,
            message='Hello'
        )

        # Make friendship
        Friend.objects.add_friend(self.normaluser, self.superuser, 'Hi')
        Friend.objects.add_friend(self.normaluser, self.user2, 'Hi')

    def test_string_representation(self):
        room = Room.objects.get(pk=self.room1.id)
        self.assertEqual(str(room), room.name)

        message = Message.objects.get(pk=1)
        self.assertEqual(str(message), f'Message from {message.user}')

    def test_get_room_list_ok(self):
        response = test_api.get(self, 'room-list', self.normaluser_credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_new_room_forbibden(self):
        response = test_api.post(self, 'room-list', {})

        self.assertEqual(response.status_code, 403)

    def test_create_new_room_empty_fields(self):
        response = test_api.post(
            self, 'room-list', {}, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)

    def test_create_new_room_invalid_fields(self):
        data = {
            'name': '',
            'label': 'test-room-1',
            'users': []
        }
        response = test_api.post(
            self, 'room-list', data, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['name'][0],
                         'This field may not be blank.')
        self.assertEqual(response.data['users']
                         [0], 'This list may not be empty.')
        self.assertEqual(response.data['label'][0],
                         'room with this label already exists.')

    def test_create_new_room_ok(self):
        data = {
            'name': 'Test room',
            'label': 'test-room',
            'users': [self.user2.id]
        }

        response = test_api.post(
            self, 'room-list', data, self.normaluser_credentials)
        self.assertEqual(response.status_code, 201)

    def test_add_empty_user_to_room(self):
        data = {
            'users': ''
        }
        response = test_api.post(
            self, 'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'New users must a list and not empty.')


    def test_add_user_to_not_exist_room(self):
        data = {
            'users': [self.user3.id]
        }
        response = test_api.post(
            self, 'room-add-users', data, self.normaluser_credentials, [100])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'],
                         'Room matching query does not exist.')

    def test_add_user_not_friend_to_room(self):
        data = {
            'users': [self.user3.id]
        }
        response = test_api.post(
            self, 'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'You do not add user is not your friend.')

    def test_add_existed_user_to_room(self):
        data = {
            'users': [self.superuser.id]
        }
        response = test_api.post(
            self, 'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'You do not add user is existed in this room.')

    def test_add_user_to_room_ok(self):
        data = {
            'users': [self.user2.id]
        }
        response = test_api.post(
            self, 'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 200)

    def test_remove_user_from_not_exist_room(self):
        data = {
            'users': []
        }
        response = test_api.delete(
            self, 'room-remove-users', data, self.normaluser_credentials, [100])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'Users must a list and not empty.')

    def test_remove_empty_user_from_room(self):
        data = {
            'users': []
        }
        response = test_api.delete(
            self, 'room-remove-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'Users must a list and not empty.')

    def test_remove_user_not_exist_from_room(self):
        data = {
            'users': [self.user3.id]
        }
        response = test_api.delete(
            self, 'room-remove-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'You do not remove user does not exist from this room.')

    def test_remove_user_from_room_ok(self):
        data = {
            'users': [self.superuser.id]
        }
        response = test_api.delete(
            self, 'room-remove-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 200)
