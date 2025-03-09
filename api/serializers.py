from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import UserProfile, APIKey
from billing.models import Plan, Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'subscription_status', 'api_calls_count', 'created_at', 'updated_at']
        read_only_fields = ['api_calls_count', 'created_at', 'updated_at']

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'is_active', 'created_at', 'last_used']
        read_only_fields = ['key', 'created_at', 'last_used']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'slug', 'price', 'api_calls_limit', 'features']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'status', 'start_date', 'end_date', 'cancel_at_period_end']
        read_only_fields = ['start_date', 'end_date']