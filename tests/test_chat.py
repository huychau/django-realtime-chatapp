from rest_framework.test import APITestCase
from chat.models import Room, Message
from user.models import Friend, User
from .helpers import HelperAPITestCase


class ChatAPITest(HelperAPITestCase):
    """
    Chat test cases
    """

    def setUp(self):
        super(ChatAPITest, self).setUp()

        self.user2 = User.objects.create_user(
            'user2', 'user2@project.com', 'password')
        self.user3 = User.objects.create_user(
            'user3', 'user3@project.com', 'password')

        self.room1 = Room.objects.create(
            user=self.normaluser,
            label='test-room-1',
            name='Test Room 1'
        )

        self.room2 = Room.objects.create(
            user=self.superuser,
            label='test-room-2',
            name='Test Room 2'
        )

        self.room1.users.add(self.normaluser, self.superuser)
        self.room2.users.add(self.user2, self.superuser)

        self.message = Message.objects.create(
            room=self.room1,
            user=self.normaluser,
            message='Hello'
        )

        self.message = Message.objects.create(
            room=self.room2,
            user=self.user2,
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
        response = self.get('room-list', self.normaluser_credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_new_room_forbidden(self):
        response = self.post('room-list', {})

        self.assertEqual(response.status_code, 403)

    def test_create_new_room_empty_fields(self):
        response = self.post(
            'room-list', {}, self.normaluser_credentials)

        self.assertEqual(response.status_code, 400)

    def test_create_new_room_invalid_fields(self):
        data = {
            'name': '',
            'label': 'test-room-1',
            'users': []
        }
        response = self.post(
            'room-list', data, self.normaluser_credentials)

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

        response = self.post(
            'room-list', data, self.normaluser_credentials)
        self.assertEqual(response.status_code, 201)

    def test_add_empty_user_to_room(self):
        data = {
            'users': ''
        }
        response = self.post(
            'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'New users must a list and not empty.')


    def test_add_user_to_not_exist_room(self):
        data = {
            'users': [self.user3.id]
        }
        response = self.post(
            'room-add-users', data, self.normaluser_credentials, [100])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'],
                         'Room matching query does not exist.')

    def test_add_user_not_friend_to_room(self):
        data = {
            'users': [self.user3.id]
        }
        response = self.post(
            'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'You do not add user is not your friend.')

    def test_add_existed_user_to_room(self):
        data = {
            'users': [self.superuser.id]
        }
        response = self.post(
            'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'You do not add user is existed in this room.')

    def test_add_user_to_room_ok(self):
        data = {
            'users': [self.user2.id]
        }
        response = self.post(
            'room-add-users', data, self.normaluser_credentials, [self.room1.id])
        self.assertEqual(response.status_code, 200)

    def test_remove_user_from_not_exist_room(self):
        data = {
            'users': []
        }
        response = self.delete(
            'room-remove-users', data, self.normaluser_credentials, [100])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'Users must a list and not empty.')

    def test_remove_empty_user_from_room(self):
        data = {
            'users': []
        }
        response = self.delete(
            'room-remove-users', data, self.normaluser_credentials,
            [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'Users must a list and not empty.')

    def test_remove_user_not_exist_from_room(self):
        data = {
            'users': [self.user3.id]
        }
        response = self.delete(
            'room-remove-users', data, self.normaluser_credentials,
            [self.room1.id])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'You do not remove user does not exist from this room.')

    def test_remove_user_from_room_ok(self):
        data = {
            'users': [self.superuser.id]
        }
        response = self.delete(
            'room-remove-users', data, self.normaluser_credentials,
            [self.room1.id])
        self.assertEqual(response.status_code, 200)

    def test_get_messages_from_not_exist_room(self):
        data = {
            'room': 100
        }
        response = self.get(
            'message-list', self.normaluser_credentials, None, data)
        self.assertEqual(response.status_code, 404)

    def test_get_messages_user_not_join_room(self):
        data = {
            'room': self.room2.id
        }
        response = self.get(
            'message-list', self.normaluser_credentials, None, data)
        self.assertEqual(response.status_code, 400)

    def test_get_messages_ok(self):
        data = {
            'room': self.room1.id
        }
        response = self.get(
            'message-list', self.normaluser_credentials, None, data)
        self.assertEqual(response.status_code, 200)

    def test_create_messages_not_join_room(self):
        data = {
            'room': self.room2.id,
            'message': 'Hello'
        }
        response = self.post(
            'message-list', data, self.normaluser_credentials)
        self.assertEqual(response.status_code, 400)

    def test_create_empty_messages(self):
        data = {
            'room': self.room1.id,
            'message': ''
        }
        response = self.post(
            'message-list', data, self.normaluser_credentials)
        self.assertEqual(response.status_code, 400)

    def test_create_messages_ok(self):
        data = {
            'room': self.room1.id,
            'message': 'Hello'
        }
        response = self.post(
            'message-list', data, self.normaluser_credentials)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], data['message'])
