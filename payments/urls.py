from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<str:plan_slug>/', views.initiate_payment, name='initiate_payment'),
    path('history/', views.payment_history, name='history'),
    path('webhook/', views.razorpay_webhook, name='webhook'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('callback/', views.payment_callback, name='callback'),
]
