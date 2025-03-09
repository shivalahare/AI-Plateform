from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='profile')
router.register(r'keys', views.APIKeyViewSet, basename='apikey')
router.register(r'plans', views.PlanViewSet, basename='plan')
router.register(r'subscription', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', views.APIRootView.as_view(), name='api-root'),
    path('', include(router.urls)),
    path('keys/generate/', views.generate_api_key, name='generate-api-key'),
    path('keys/<int:key_id>/revoke/', views.revoke_api_key, name='revoke-api-key'),
]
