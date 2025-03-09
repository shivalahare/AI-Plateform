from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('subscription/', views.subscription, name='subscription'),
    path('change-plan/<str:plan_slug>/', views.change_plan, name='change_plan'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),
    path('reactivate-subscription/', views.reactivate_subscription, name='reactivate_subscription'),
    path('invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
]
