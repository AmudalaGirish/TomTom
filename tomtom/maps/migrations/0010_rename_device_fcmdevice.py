# Generated by Django 5.0.2 on 2024-05-09 09:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0009_sampleinvoice_device'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Device',
            new_name='FCMDevice',
        ),
    ]