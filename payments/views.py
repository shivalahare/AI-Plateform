import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from .services import RazorpayService
from billing.models import Plan, Subscription, Invoice
from .models import Payment
import logging

logger = logging.getLogger(__name__)

razorpay_service = RazorpayService()

@login_required
def initiate_payment(request, plan_slug):
    plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)
    
    if plan.price <= 0:
        return redirect('billing:change_plan', plan_slug=plan_slug)
    
    try:
        # Create Razorpay Order - let service handle paise conversion
        order = razorpay_service.create_order(plan.price)
        
        # Create Payment record (store original amount in rupees)
        payment = Payment.objects.create(
            user=request.user,
            amount=float(plan.price),
            razorpay_order_id=order['id'],
            status='created'
        )
        
        context = {
            'plan': plan,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': order['id'],
            'amount': int(float(plan.price) * 100),  # Convert to paise for frontend
            'currency': 'INR',
            'callback_url': request.build_absolute_uri(reverse('payments:callback'))
        }
        
        return render(request, 'payments/checkout.html', context)
        
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        if "Network error" in str(e):
            messages.error(request, "Unable to connect to payment service. Please check your internet connection and try again.")
        else:
            messages.error(request, "Error initiating payment. Please try again later.")
        return redirect('billing:pricing')

@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook notifications"""
    if request.method == "POST":
        try:
            # Verify webhook signature
            webhook_signature = request.headers.get('X-Razorpay-Signature')
            webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
            
            # Get the raw body
            webhook_data = request.body.decode('utf-8')
            
            # Verify webhook
            razorpay_service.client.utility.verify_webhook_signature(
                webhook_data,
                webhook_signature,
                webhook_secret
            )
            
            # Process webhook data
            data = json.loads(webhook_data)
            event = data.get('event')
            
            if event == 'payment.captured':
                payment_id = data['payload']['payment']['entity']['id']
                payment = Payment.objects.get(razorpay_payment_id=payment_id)
                payment.status = 'captured'
                payment.save()
                
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def payment_success(request):
    """Handle successful payment redirect"""
    payment_id = request.GET.get('razorpay_payment_id')
    if payment_id:
        try:
            payment = Payment.objects.get(razorpay_payment_id=payment_id)
            messages.success(request, 'Payment successful! Your subscription is now active.')
            return redirect('billing:subscription')
        except Payment.DoesNotExist:
            messages.error(request, 'Payment verification failed.')
    
    return redirect('billing:pricing')

@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    messages.warning(request, 'Payment was cancelled.')
    return redirect('billing:pricing')

@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})

@login_required
def cancel_subscription(request, subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)
    
    if subscription.user != request.user:
        return JsonResponse({'error': 'You do not have permission to cancel this subscription.'}, status=403)

@csrf_exempt
@login_required
def payment_callback(request):
    """Handle payment callback from Razorpay"""
    if request.method == "POST":
        try:
            # Verify payment signature
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Verify signature
            razorpay_service.client.utility.verify_payment_signature({
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            })
            
            # Update payment record
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.razorpay_payment_id = payment_id
            payment.status = 'completed'
            payment.save()
            
            messages.success(request, 'Payment successful! Your subscription is now active.')
            return redirect('billing:subscription')
            
        except Exception as e:
            logger.error(f"Payment callback error: {str(e)}")
            messages.error(request, 'Payment verification failed.')
            return redirect('billing:pricing')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
