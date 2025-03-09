from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import (
    UserProfileSerializer, APIKeySerializer,
    PlanSerializer, SubscriptionSerializer
)
from accounts.models import UserProfile, APIKey
from billing.models import Plan, Subscription
from .permissions import IsOwner

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_api_key(request):
    name = request.data.get('name', 'Default Key')
    api_key = APIKey.objects.create(
        user=request.user,
        name=name
    )
    serializer = APIKeySerializer(api_key)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_api_key(request, key_id):
    api_key = get_object_or_404(APIKey, id=key_id, user=request.user)
    api_key.is_active = False
    api_key.save()
    
    # Return the updated API key data
    serializer = APIKeySerializer(api_key)
    return Response(serializer.data, status=status.HTTP_200_OK)

class APIRootView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'profile': request.build_absolute_uri('/api/profile/'),
            'api_keys': request.build_absolute_uri('/api/keys/'),
            'plans': request.build_absolute_uri('/api/plans/'),
            'subscription': request.build_absolute_uri('/api/subscription/'),
        })
