from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
import asyncio
from django.core.exceptions import ValidationError
from user.models import User
from chatapp.constants import CHAT_ROOM_PREFIX
from .views import MessageViewSet
from .models import Message, Room


class ChatConsumer(WebsocketConsumer):

    def init_chat(self):
        """
        Init chat room by check user, room
        """

        self.user = self.scope['user']

        # Check not valid user
        if not self.user.is_authenticated:
            self.send_error_message('Require login.')
            return

        # Check user in the room
        self.room_id = int(self.scope['url_route']['kwargs']['room'])
        self.room_group_name = f'{CHAT_ROOM_PREFIX}{self.room_id}'

        try:

            self.room = Room.objects.get(pk=self.room_id)
            self.room_users = self.room.users.all()

            if self.user not in self.room_users:
                self.send_error_message('User is not in this room.')
                return

            return True

        except (ValidationError, Room.DoesNotExist) as e:
            self.send_error_message(str(e))
            return False

        return True

    def fetch_messages(self, data):
        """
        Fetch latest messages form a room
        """

        try:

            # Get messages form a room
            messages = Message.objects.last_messages(data['room'])

            content = {
                'command': 'messages',
                'messages': self.messages_to_json(messages)
            }
            self.send_message(content)

        except ValidationError as e:
            return self.send_error_message(str(e))

    def new_message(self, data):
        """
        Create new message
        """

        room = Room.objects.get(pk=self.room_id)
        message = Message.objects.create(
            user=self.user,
            message=data['message'],
            room=room)

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        """
        Format message list to json
        """

        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        """
        Format message instance to json
        """

        return {
            'user': message.user.username,
            'message': message.message,
            'created': str(message.created)
        }

    def send_error_message(self, message):
        """
        Send error message
        """

        content = {
            'command': 'error_message',
            'message': message
        }

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'error_message',
                'message': content
            }
        )

    def error_message(self, event):
        """
        Handler for error message
        """
        message = event['message']
        self.send(text_data=json.dumps(message))

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'error_message': error_message,
    }

    def connect(self):
        """
        Connect to unique channel
        """

        self.init_chat()

        # Check init success
        if hasattr(self, 'room_group_name'):

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()


    def disconnect(self, close_code):
        """
        Disconnect form a channel
        """

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        """
        Receive message
        """

        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_message(self, message):
        """
        Hander for message
        """
        self.send(text_data=json.dumps(message))

    def send_chat_message(self, message):
        """
        Send chat message
        """
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        """
        Send message to channel
        """
        message = event['message']
        self.send(text_data=json.dumps(message))
