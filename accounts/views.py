from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import SignUpForm, UserProfileForm
from .models import APIKey
from dashboard.models import UserActivity 
from billing.models import Subscription
from django.utils import timezone
import uuid

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard:home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            # Update UserProfile model fields
            profile = form.save(commit=False)
            
            # Properly handle notification preferences
            selected_preferences = form.cleaned_data.get('notification_preferences', [])
            profile.notification_preferences = {
                'email_updates': 'email_updates' in selected_preferences,
                'product_news': 'product_news' in selected_preferences,
                'security_alerts': 'security_alerts' in selected_preferences,
                'usage_reports': 'usage_reports' in selected_preferences
            }
            
            profile.save()
            # Add activity for profile update
            UserActivity.objects.create(
                user=request.user,
                activity_type='profile_update',
                description='Updated profile information'
            )
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        # Initialize form with current preferences
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'notification_preferences': [
                pref for pref, enabled in 
                request.user.userprofile.notification_preferences.items() 
                if enabled
            ]
        }
        form = UserProfileForm(instance=request.user.userprofile, initial=initial_data)

    # Get subscription information - UPDATED THIS PART
    try:
        subscription = Subscription.objects.get(
            user=request.user,
            status='active'
        )
    except Subscription.DoesNotExist:
        subscription = None

    # Get active API keys
    api_keys = APIKey.objects.filter(user=request.user, is_active=True)

    # Calculate API usage percentage
    api_calls_limit = subscription.plan.api_calls_limit if subscription else 100
    api_calls_used = request.user.userprofile.api_calls_count
    usage_percentage = min(round((api_calls_used / api_calls_limit) * 100), 100)

    context = {
        'form': form,
        'api_keys': api_keys,
        'subscription': subscription,
        'api_calls_used': api_calls_used,
        'api_calls_limit': api_calls_limit,
        'usage_percentage': usage_percentage
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def generate_api_key(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Default Key')
        api_key = APIKey.objects.create(
            user=request.user,
            key=str(uuid.uuid4()),
            name=name
        )
        messages.success(request, 'API key generated successfully!')
    return redirect('accounts:profile')

@login_required
def settings(request):
    if request.method == 'POST':
        # Handle any settings updates here
        pass
    
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/settings.html', context)
