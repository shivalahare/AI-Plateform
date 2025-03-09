from django.core.management.base import BaseCommand
from django.utils import timezone
from billing.models import Subscription

class Command(BaseCommand):
    help = 'Reset API calls count for subscriptions in new billing period'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        active_subscriptions = Subscription.objects.filter(
            status='active',
            end_date__gte=now
        )

        for subscription in active_subscriptions:
            subscription.reset_api_calls_count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Reset API calls count for user: {subscription.user.username}'
                )
            )