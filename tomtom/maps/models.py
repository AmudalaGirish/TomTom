# models.py

from django.db import models

class Ride(models.Model):
    pickup_address = models.CharField(max_length=255)
    drop_address = models.CharField(max_length=255)
    # Add the following fields for storing coordinates
    pickup_latitude = models.FloatField(default=0.0)
    pickup_longitude = models.FloatField(default=0.0)
    drop_latitude = models.FloatField(default=0.0)  # Set your desired default value
    drop_longitude = models.FloatField(default=0.0)

class Employees(models.Model):
    emp_id = 