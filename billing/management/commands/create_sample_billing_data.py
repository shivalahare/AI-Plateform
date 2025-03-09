from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from billing.models import Plan, Subscription, Invoice
from datetime import timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Creates sample billing data including plans, subscriptions, and invoices'

    def handle(self, *args, **kwargs):
        # Create Plans
        plans_data = [
            {
                'name': 'Free Tier',
                'slug': 'free-tier',
                'price': Decimal('0.00'),
                'api_calls_limit': 100,
                'features': {
                    'max_tokens_per_request': 1000,
                    'supported_models': ['gpt-3.5-turbo'],
                    'priority_support': False,
                    'custom_models': False
                }
            },
            {
                'name': 'Basic Plan',
                'slug': 'basic-plan',
                'price': Decimal('29.99'),
                'api_calls_limit': 1000,
                'features': {
                    'max_tokens_per_request': 2000,
                    'supported_models': ['gpt-3.5-turbo', 'gpt-4'],
                    'priority_support': False,
                    'custom_models': False
                }
            },
            {
                'name': 'Professional Plan',
                'slug': 'professional-plan',
                'price': Decimal('99.99'),
                'api_calls_limit': 5000,
                'features': {
                    'max_tokens_per_request': 4000,
                    'supported_models': ['gpt-3.5-turbo', 'gpt-4', 'claude-v2'],
                    'priority_support': True,
                    'custom_models': False
                }
            },
            {
                'name': 'Enterprise Plan',
                'slug': 'enterprise-plan',
                'price': Decimal('499.99'),
                'api_calls_limit': 50000,
                'features': {
                    'max_tokens_per_request': 8000,
                    'supported_models': ['gpt-3.5-turbo', 'gpt-4', 'claude-v2', 'custom'],
                    'priority_support': True,
                    'custom_models': True
                }
            }
        ]

        # Create Plans
        created_plans = []
        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults={
                    'name': plan_data['name'],
                    'price': plan_data['price'],
                    'api_calls_limit': plan_data['api_calls_limit'],
                    'features': plan_data['features']
                }
            )
            created_plans.append(plan)
            if created:
                self.stdout.write(f'Created plan: {plan.name}')

        # Create Subscriptions and Invoices for existing users
        users = User.objects.all()
        subscription_statuses = ['active', 'cancelled', 'expired', 'past_due']
        invoice_statuses = ['draft', 'open', 'paid', 'failed', 'void']

        for user in users:
            # Create Subscription
            plan = random.choice(created_plans)
            status = random.choice(subscription_statuses)
            start_date = timezone.now() - timedelta(days=random.randint(1, 365))
            end_date = start_date + timedelta(days=30)

            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'status': status,
                    'start_date': start_date,
                    'end_date': end_date,
                    'cancel_at_period_end': random.choice([True, False])
                }
            )
            if created:
                self.stdout.write(f'Created subscription for user: {user.username}')

            # Create Invoices
            for i in range(random.randint(1, 5)):
                invoice_date = start_date + timedelta(days=30 * i)
                status = random.choice(invoice_statuses)
                paid_at = invoice_date + timedelta(days=random.randint(1, 5)) if status == 'paid' else None

                invoice = Invoice.objects.create(
                    user=user,
                    subscription=subscription,
                    amount=plan.price,
                    status=status,
                    due_date=invoice_date.date(),
                    paid_at=paid_at
                )
                self.stdout.write(f'Created invoice #{invoice.id} for user: {user.username}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample billing data'))