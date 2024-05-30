import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Profile, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
        else:
            self.room_group_name = f'chat_{self.user.username}'

            # Join the user's personal group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # If user is admin, join the admin group
            is_admin = await self.is_admin()
            if is_admin:
                await self.channel_layer.group_add(
                    'admin_group',
                    self.channel_name
                )

            await self.accept()

    async def disconnect(self, close_code):
        # Leave the user's personal group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # If user is admin, leave the admin group
        is_admin = await self.is_admin()
        if is_admin:
            await self.channel_layer.group_discard(
                'admin_group',
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'chat':
            message = text_data_json['message']
            recipient_username = text_data_json.get('recipient')
            if recipient_username:
                recipient = await self.get_user_by_username(recipient_username)
                await self.send_to_user(message, recipient)
            else:
                await self.send_to_admins(message)
        elif message_type == 'call':
            await self.handle_call_signal(text_data_json)
        elif message_type == 'call_state':
            await self.handle_call_state(text_data_json)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username
        }))

    async def call_signal(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call',
            'signal': event['signal'],
            'username': event['username']
        }))

    async def call_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_state',
            'state': event['state'],
            'username': event['username']
        }))

    async def send_to_admins(self, message):
        await self.channel_layer.group_send(
            'admin_group',
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )

    async def send_to_user(self, message, recipient):
        recipient_group_name = f'chat_{recipient.username}'

        await self.channel_layer.group_send(
            recipient_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )

    async def handle_call_signal(self, data):
        recipient_username = data['recipient']
        recipient = await self.get_user_by_username(recipient_username)
        recipient_group_name = f'chat_{recipient.username}'
        await self.channel_layer.group_send(
            recipient_group_name,
            {
                'type': 'call_signal',
                'signal': data['signal'],
                'username': self.user.username
            }
        )

    async def handle_call_state(self, data):
        recipient_username = data['recipient']
        state = data['state']
        recipient = await self.get_user_by_username(recipient_username)
        recipient_group_name = f'chat_{recipient.username}'
        await self.channel_layer.group_send(
            recipient_group_name,
            {
                'type': 'call_state',
                'state': state,
                'username': self.user.username
            }
        )

    @sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def get_user_profile(self, user):
        return user.profile

    async def is_admin(self):
        profile = await self.get_user_profile(self.user)
        return profile.role == 'admin'
