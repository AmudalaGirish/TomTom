import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Profile, Message

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         if not self.user.is_authenticated:
#             await self.close()
#         else:
#             self.room_group_name = f'chat_{self.user.username}'

#             print("channel_layer:", self.channel_layer)
#             print("room_group_name:", self.room_group_name)
#             print("channel_name:", self.channel_name)

#             # Join the user's personal group
#             await self.channel_layer.group_add(
#                 self.room_group_name,
#                 self.channel_name
#             )

#             # If user is admin, join the admin group
#             is_admin = await self.is_admin()
#             if is_admin:
#                 await self.channel_layer.group_add(
#                     'admin_group',
#                     self.channel_name
#                 )
#                 print("channel_layer inside is_admin:", self.channel_layer)
#                 print("inside is_admin, channel_name:", self.channel_name)
            
#             await self.accept()

#     async def disconnect(self, close_code):
#         # Leave the user's personal group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#         print("inside disconnect, room_group_name:", self.room_group_name)
#         print("inside disconnect, channel_name:", self.channel_name)
#         # If user is admin, leave the admin group
#         is_admin = await self.is_admin()
#         if is_admin:
#             await self.channel_layer.group_discard(
#                 'admin_group',
#                 self.channel_name
#             )
#             print("inside disconnect. is_admin, channel_name:", self.channel_name)

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         # If the sender is an employee, broadcast to all admins
#         is_admin = await self.is_admin()
#         if not is_admin:
#             await self.send_to_admins(message)
#         else:
#             recipient_username = text_data_json['recipient']
#             recipient = await self.get_user_by_username(recipient_username)
#             await self.send_to_user(message, recipient)

#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']

#         await self.send(text_data=json.dumps({
#             'message': message,
#             'username': username
#         }))

#     async def send_to_admins(self, message):
#         await self.channel_layer.group_send(
#             'admin_group',
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': self.user.username
#             }
#         )

#         # Save message to the database
#         # await self.save_message(self.user, None, message)

#     async def send_to_user(self, message, recipient):
#         recipient_group_name = f'chat_{recipient.username}'

#         await self.channel_layer.group_send(
#             recipient_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': self.user.username
#             }
#         )

#         # Save message to the database
#         # await self.save_message(self.user, recipient, message)

#     @sync_to_async
#     def get_user_by_username(self, username):
#         return User.objects.get(username=username)

#     @sync_to_async
#     def get_user_profile(self, user):
#         return user.profile

#     async def is_admin(self):
#         profile = await self.get_user_profile(self.user)
#         return profile.role == 'admin'

#     # @sync_to_async
#     # def save_message(self, sender, recipient, message):
#     #     Message.objects.create(sender=sender, recipient=recipient, message)


#######################################################

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
        else:
            self.room_group_name = f'chat_{self.user.username}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            is_admin = await self.is_admin()
            if is_admin:
                await self.channel_layer.group_add(
                    'admin_group',
                    self.channel_name
                )
                print(f"Admin {self.user.username} joined admin group")
            
            print(f"User {self.user.username} connected and joined group {self.room_group_name}")
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        is_admin = await self.is_admin()
        if is_admin:
            await self.channel_layer.group_discard(
                'admin_group',
                self.channel_name
            )
            print(f"Admin {self.user.username} left admin group")
        
        print(f"User {self.user.username} disconnected from group {self.room_group_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        recipient_username = text_data_json.get('recipient')
        private_chat = text_data_json.get('private_chat', False)

        print(f"Message received from {self.user.username}: {message}")

        if private_chat and recipient_username:
            recipient = await self.get_user_by_username(recipient_username)
            await self.send_to_user_private(message, recipient)
        else:
            is_admin = await self.is_admin()
            if not is_admin:
                await self.send_to_admins(message)
            else:
                recipient = await self.get_user_by_username(recipient_username)
                await self.send_to_user_private(message, recipient)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
        print(f"Sent message to {self.user.username}: {message}")

    async def send_to_admins(self, message):
        await self.channel_layer.group_send(
            'admin_group',
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )
        print(f"Sent message to admin group from {self.user.username}: {message}")

    async def send_to_user_private(self, message, recipient):
        private_room_name = self.get_private_room_name(self.user, recipient)

        await self.channel_layer.group_add(
            private_room_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            private_room_name,
            f'chat_{recipient.username}'
        )

        await self.channel_layer.group_send(
            private_room_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )
        print(f"Sent private message from {self.user.username} to {recipient.username}: {message}")

    def get_private_room_name(self, user1, user2):
        usernames = sorted([user1.username, user2.username])
        return f'private_chat_{"_".join(usernames)}'

    @sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def get_user_profile(self, user):
        return user.profile

    async def is_admin(self):
        profile = await self.get_user_profile(self.user)
        return profile.role == 'admin'
