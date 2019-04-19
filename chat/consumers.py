from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
import asyncio
from rest_framework.exceptions import ValidationError, NotFound
from chatapp.constants import CHAT_ROOM_PREFIX
from .views import MessageViewSet
from .models import Message, Room
from chatapp import constants
from django.core import serializers


class ChatConsumer(WebsocketConsumer):
    """
    Chat consumer
    """

    def init_chat(self):
        """
        Init chat room by check user, room
        """

        self.user = self.scope['user']

        # Check not valid user
        if not self.user or not self.user.is_authenticated:
            self.send_error_message('Require login.')
            return

        # Check user in the room
        self.room_id = int(self.scope['url_route']['kwargs']['room'])
        self.room_group_name = f'{CHAT_ROOM_PREFIX}{self.room_id}'

        try:
            self.room = Room.objects.get_room(pk=self.room_id)
            self.room_users = self.room.users.all()

            if self.user not in self.room_users:
                self.send_error_message('User is not in this room.')

        except (ValidationError, NotFound) as e:
            self.send_error_message(str(e))

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

    def json_serialize(self, data):
        """
        Serializer data to json
        """
        return json.loads(serializers.serialize('json', data))

    def fetch_data(self, data):
        """
        Fetch latest messages form a room
        """

        try:

            # Get messages form a room
            messages = Message.objects.messages(self.user,
                self.room.id)[:constants.MESSAGE_MAXIMUM][::-1]

            # Something for client
            room_serializer = self.json_serialize([self.room, ])
            users_serializer = self.json_serialize(self.room_users)
            messages_serializer = self.json_serialize(messages)

            content = {
                'command': 'fetch_data',
                'messages': messages_serializer,
                'room': room_serializer[0],
                'room_users': users_serializer
            }

            self.send_message(content)

        except (ValidationError, AttributeError) as e:
            return self.send_error_message('Room matching query does not exist.')

    def new_message(self, data):
        """
        Create new message
        """

        msg = data['message']

        if msg:

            message = Message.objects.create(
                user=self.user,
                message=data['message'],
                room=self.room)

            print(message)

            message_serializer = self.json_serialize([message, ])

            print(message_serializer)

            content = {
                'command': 'new_message',
                'message': message_serializer[0]
            }
            return self.send_chat_message(content)
        else:
            return self.send_error_message('Message content is require.')

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

    def send_message(self, message):
        """
        Handler for message
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

    # Command to send to client
    commands = {
        'fetch_data': fetch_data,
        'new_message': new_message,
        'error_message': error_message
    }
