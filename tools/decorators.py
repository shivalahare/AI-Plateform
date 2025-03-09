from functools import wraps
from django.http import JsonResponse
from billing.models import Subscription
from django.utils import timezone

def check_subscription_limits(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get user's active subscription
        try:
            subscription = Subscription.objects.get(
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

            # Check API calls limit
            current_usage = request.user.userprofile.api_calls_count
            if current_usage >= subscription.plan.api_calls_limit:
                return JsonResponse({
                    'success': False,
                    'error': 'You have reached your API calls limit for this billing period.',
                    'limit': subscription.plan.api_calls_limit,
                    'usage': current_usage
                }, status=429)  # 429 Too Many Requests

        except Subscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found. Please subscribe to use this feature.'
            }, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper