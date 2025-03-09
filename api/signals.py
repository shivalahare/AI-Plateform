import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver
from accounts.models import APIKey

@receiver(pre_save, sender=APIKey)
def generate_api_key(sender, instance, **kwargs):
    """Generate a UUID-based API key if not already set."""
    if not instance.key:
        instance.key = str(uuid.uuid4())