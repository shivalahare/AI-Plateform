from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    api_calls_limit = models.IntegerField()
    features = models.JSONField(default=list)  # Changed to default=list
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']  # Default ordering by price

    def __str__(self):
        return self.name

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('past_due', 'Past Due'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    def reset_api_calls_count(self):
        """Reset the API calls count at the start of new billing period"""
        self.user.userprofile.api_calls_count = 0
        self.user.userprofile.save()

    def save(self, *args, **kwargs):
        # If this is a new subscription or the end_date has changed
        if not self.pk or self._state.adding or (
            self.pk and self.end_date != Subscription.objects.get(pk=self.pk).end_date
        ):
            self.reset_api_calls_count()
        super().save(*args, **kwargs)

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('void', 'Void'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            next_number = (last_invoice.id + 1) if last_invoice else 1
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m')}-{next_number:04d}"
        super().save(*args, **kwargs)
