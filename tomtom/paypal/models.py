from django.db import models

class PayPalTransaction(models.Model):
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id

class Transaction_paypal(models.Model):
    invoice_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    order_status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=255)
    transaction_status = models.CharField(max_length=20)