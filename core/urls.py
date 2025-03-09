from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('tools/', include('tools.urls')),
    path('billing/', include('billing.urls')),
    path('api/', include('api.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('pricing/', TemplateView.as_view(template_name='billing/pricing.html'), name='pricing'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
