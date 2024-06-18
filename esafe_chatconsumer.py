import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve the JWT token from the query parameters
        query_params = self.scope['query_string'].decode()
        token = query_params.split('=')[1]

        # Validate the JWT token
        try:
            access_token = AccessToken(token)
            self.user = await sync_to_async(User.objects.get)(id=access_token['user_id'])
            print(f"User authenticated: {self.user}")
            self.room_group_name = f'chat_{self.user.username}'
        except (InvalidToken, User.DoesNotExist):
            # If the token is invalid or the user does not exist, close the connection
            await self.close()
            return

        # If authentication is successful, continue with the connection process
        await self.accept()
        print(f"WebSocket connection established for user: {self.user.username}")

        # Join the user's personal group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("####################### : user personal group")
        print("Channel_layer:", self.channel_layer)
        print("room_group_name:", self.room_group_name)
        print("channel Name:", self.channel_name)
        # If user is admin, join the admin group
        if await self.is_admin():
            await self.channel_layer.group_add(
                'admin_group',
                self.channel_name
            )
            print("###################### : is_admin() true:")
            print("Channel_layer:", self.channel_layer)
            print("room_group_name:", self.room_group_name)
            print("channel Name:", self.channel_name)

    async def disconnect(self, close_code):
        # Leave the user's personal group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # If user is admin, leave the admin group
        if await self.is_admin():
            await self.channel_layer.group_discard(
                'admin_group',
                self.channel_name
            )
            print(f"WebSocket connection closed for admin group: {self.user.username}")
        print(f"WebSocket connection closed for user group: {self.user.username}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        recipient_username = text_data_json.get('recipient')

        print("######################### : under receive")
        print("message:", message,"recipient:", recipient_username,"sender:", self.user.username)

        # If the sender is an admin, send to the specified recipient
        if await self.is_admin():
            if recipient_username:
                recipient = await self.get_user_by_username(recipient_username)
                print("recipient:", recipient)
                await self.send_to_user(message, recipient)
        else:
            # If the sender is not an admin, broadcast to all admins
            await self.send_to_admins(message)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
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
        print(f"message sent to admin, username: {self.user.username}, message: {message}")
        

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
        print(f"message sent to user, username: {self.user.username}, message:{message}")

    @sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def get_user_groups(self, user):
        return list(user.groups.all())  # Convert QuerySet to list

    async def is_admin(self):
        groups = await self.get_user_groups(self.user)
        print("user groups:", groups)
        for group in groups:
            if group.name in ['AppAdmin', 'ClientAdmin', 'MasterAdmin', 'Super Admin']:
                return True
        return False