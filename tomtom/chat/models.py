from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
class Profile(models.Model):
    USER_ROLES = (
        ('emp', 'Employee'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=5, choices=USER_ROLES)

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username if self.recipient else 'Admins'}: {self.message}"

