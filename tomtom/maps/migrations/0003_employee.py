# Generated by Django 5.0.2 on 2024-02-28 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0002_alter_ride_drop_latitude_alter_ride_drop_longitude_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emp_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
