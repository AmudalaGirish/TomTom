from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from maps.utils import get_coordinates


class Ride(models.Model):
    pickup_address = models.CharField(max_length=255)
    pickup_address_1 = models.CharField(max_length=255, blank=True, null=True)
    pickup_address_2 = models.CharField(max_length=255, blank=True, null=True)
    drop_address = models.CharField(max_length=255)
    # Add the following fields for storing coordinates
    pickup_latitude = models.FloatField(default=0.0)
    pickup_longitude = models.FloatField(default=0.0)
    pickup_latitude_1 = models.FloatField(default=0.0, blank=True, null=True)
    pickup_longitude_1 = models.FloatField(default=0.0, blank=True, null=True)
    pickup_latitude_2 = models.FloatField(default=0.0, blank=True, null=True)
    pickup_longitude_2 = models.FloatField(default=0.0, blank=True, null=True)
    drop_latitude = models.FloatField(default=0.0)
    drop_longitude = models.FloatField(default=0.0)


class Employee(models.Model):
    emp_id = models.CharField(
        max_length=20, unique=True, verbose_name=_('Employee ID'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    address = models.TextField(verbose_name=_('Address'))
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name=_('Latitude'))
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name=_('Longitude'))

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Employee)
def update_employee_coordinates(sender, instance, **kwargs):
    # Automatically update latitude and longitude before saving the Employee instance
    instance.latitude, instance.longitude = get_coordinates(instance.address)


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    address = models.TextField(verbose_name=_('Address'))
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name=_('Latitude'))
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name=_('Longitude'))

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Client)
def update_client_coordinates(sender, instance, **kwargs):
    # Automatically update latitude and longitude before saving the Client instance
    instance.latitude, instance.longitude = get_coordinates(instance.address)


class Payment(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    amount = models.IntegerField()
    order_id = models.CharField(max_length=100, verbose_name=_('Order ID'))
    razorpay_payment_id = models.CharField(
        max_length=100, verbose_name=_('Razorpay Payment ID'))
    paid = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
