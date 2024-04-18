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

from django.db import models

class Transaction(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()
    currency = models.CharField(max_length=3)
    receipt_id = models.CharField(max_length=40, blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    partial_payment = models.BooleanField(default=False)
    first_payment_min_amount = models.IntegerField(blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=[
        ('created', 'Created'), ('attempted', 'Attempted'), ('paid', 'Paid')
    ])
    razorpay_payment_id = models.CharField(max_length=100, unique=True)
    razorpay_signature = models.CharField(max_length=120)
    payment_status = models.CharField(max_length=20, choices=[
        ('created', 'Created'), ('authorized', 'Authorized'), ('captured', 'Captured'),
        ('refunded', 'Refunded'), ('failed', 'Failed')
    ])
    payment_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order: {self.order_id}"

class SampleInvoice(models.Model):
    invoice_id = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField()
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=100)
    customer_address = models.TextField()
    item = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_status = models.CharField(max_length=20, choices=[
        ('created', 'Created'), ('paid', 'Paid')
    ])
    invoice_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice: {self.invoice_id}"