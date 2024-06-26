# Generated by Django 5.0.2 on 2024-06-11 02:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0004_employee_stu_teacher'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f1', models.CharField(max_length=100)),
                ('f2', models.IntegerField()),
                ('f3', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='StrandardModel',
            fields=[
                ('basicmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='learn.basicmodel')),
                ('f4', models.CharField(max_length=100)),
                ('f5', models.IntegerField()),
                ('f6', models.FloatField()),
            ],
            bases=('learn.basicmodel',),
        ),
    ]
