import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.core.cache import cache

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
            print("room_group_name: admin_group")

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

        # # Clear current_admin value from cache
        # if not await self.is_admin():
        #     cache.delete(f'{self.user.username}_current_admin')
        #     print(f"Cleared current_admin value from cache for user: {self.user.username}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("text_data_json:", text_data_json)
        message = text_data_json['message']
        recipient_username = text_data_json.get('recipient')
        # current_admin = text_data_json.get('currentadmin')

        print("######################### : under receive")
        print("message:", message,"recipient:", recipient_username,"sender:", self.user.username)
        
        # Save the message in the database
        await self.save_message(self.user, message, recipient_username)

        # If the sender is an admin, send to the specified recipient
        if await self.is_admin():
            if recipient_username:
                recipient = await self.get_user_by_username(recipient_username)
                print("recipient:", recipient)
                await self.send_to_user(message, recipient)
                # Store current_admin value in cache
                # cache.set(f'{recipient_username}_current_admin', current_admin)
                # print("####################################")
                # print(f"cache is set: {recipient_username}_current_admin")
        else:
            # If the sender is not an admin, broadcast to all admins
            await self.send_to_admins(message)
            # # # If the sender is not an admin, check for current_admin value in cache
            # # current_admin = cache.get(f'{self.user.username}_current_admin')
            # # print("#####################################")
            # # print("user is not admin get current_admin in cache:", current_admin)
            # if current_admin: # check in cache
            #     await self.send_to_current_admin(message, current_admin)
            # else:
            #     # If the sender is not an admin, broadcast to all admins
            #     await self.send_to_admins(message)
        print(f"message is recived from browser: recipient: {recipient_username}, sender: {self.user.username}")

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        user_id = event['user_id']
        room_name = event['room_name']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'user_id': user_id,
            'room_name': room_name
        }))

    async def send_to_admins(self, message):
        await self.channel_layer.group_send(
            'admin_group',
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'user_id': self.user.id,
                'room_name':self.room_group_name
            }
        )
        print(f"message sent to all admins, sender: {self.user.username}, room name: admin_group")

    async def send_to_current_admin(self, message, current_admin):
        current_admin_group_name = f'chat_{current_admin}'
        await self.channel_layer.group_send(
            current_admin_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'user_id': self.user.id,
                'room_name': current_admin_group_name
            }
        )
        print(f"message sent to current admin {current_admin}, sender: {self.user.username}, room name: {current_admin_group_name}")

    async def send_to_user(self, message, recipient):
        recipient_group_name = f'chat_{recipient.username}'

        await self.channel_layer.group_send(
            recipient_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'user_id': self.user.id,
                'room_name': recipient_group_name
            }
        )
        print(f"message sent to user, sender: {self.user.username}, receiver: {recipient.username}, room name:{recipient_group_name}")

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
    
    # @sync_to_async
    # def save_message(self, user, content):
    #     room, created = ChatRoom.objects.get_or_create(name=f'chat_{user.username}', status= 'active')
    #     Message.objects.create(room=room, user=user, content=content)
    #     print(f"Message is saved in room:{room}, created:{created} with message:{content}")

    @sync_to_async
    def save_message(self, user, content, recipient_username=None):
        if recipient_username:
            # room_name = self.get_room_name(user.username, recipient_username)
            room_name = f'chat_{recipient_username}'
            print(f"$$$$$$$$$$$$$$$$$$$$$ : recipient user: {recipient_username}")
            print("Room Name:", room_name)
            room, created = ChatRoom.objects.get_or_create(name=room_name, status='active')
            recipient = User.objects.get(username=recipient_username)
            room.members.add(user, recipient)
        else:
            room_name = f'chat_{user.username}'
            print(f"$$$$$$$$$$$$$$$$$$$$$$$$: no recipent")
            print(f"Room Name: {room_name}")
            room, created = ChatRoom.objects.get_or_create(name=room_name, status='active')
            room.members.add(user)
        
        Message.objects.create(room=room, user=user, content=content)
        print(f"Message is saved in room: {room}, created: {created} with message: {content}")
