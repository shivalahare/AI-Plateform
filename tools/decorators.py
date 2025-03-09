from functools import wraps
from django.http import JsonResponse
from billing.models import Subscription
from django.utils import timezone
from django.db import transaction

def check_subscription_limits(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        with transaction.atomic():  # Add transaction to prevent race conditions
            # Get user's active subscription with select_for_update to lock the row
            try:
                subscription = Subscription.objects.select_for_update().get(
                    user=request.user,
                    status='active',
                    start_date__lte=timezone.now(),
                    end_date__gte=timezone.now()
                )
                
                # Check if subscription is cancelled
                if subscription.cancel_at_period_end:
                    return JsonResponse({
                        'success': False,
                        'error': 'Your subscription is scheduled for cancellation. Please reactivate to continue.'
                    }, status=403)

                # Get current usage and check against limit
                current_usage = request.user.userprofile.api_calls_count
                if current_usage >= subscription.plan.api_calls_limit:
                    return JsonResponse({
                        'success': False,
                        'error': 'You have reached your API calls limit for this billing period.',
                        'limit': subscription.plan.api_calls_limit,
                        'usage': current_usage
                    }, status=429)  # 429 Too Many Requests

                # Increment the API calls count BEFORE processing the request
                request.user.userprofile.api_calls_count += 1
                request.user.userprofile.save()

            except Subscription.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'No active subscription found. Please subscribe to use this feature.'
                }, status=403)

            # Only proceed with the view if all checks pass
            return view_func(request, *args, **kwargs)
    return wrapper
