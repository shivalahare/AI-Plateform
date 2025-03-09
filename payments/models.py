from django.db import models
from django.contrib.auth.models import User
from billing.models import Plan, Subscription, Invoice

class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    invoice = models.OneToOneField(Invoice, on_delete=models.SET_NULL, null=True)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"

    def update_invoice_status(self):
        """Update associated invoice status based on payment status"""
        if not self.invoice:
            return

        status_mapping = {
            'captured': 'paid',
            'failed': 'failed',
            'refunded': 'void'
        }

        if self.status in status_mapping:
            self.invoice.status = status_mapping[self.status]
            self.invoice.paid_at = self.updated_at if self.status == 'captured' else None
            self.invoice.save()
# Create your models here.
