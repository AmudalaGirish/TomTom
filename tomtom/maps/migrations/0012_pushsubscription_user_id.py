# Generated by Django 5.0.2 on 2024-05-14 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0011_pushsubscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushsubscription',
            name='user_id',
            field=models.IntegerField(default=0),
        ),
    ]
