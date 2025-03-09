from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tool_list, name='list'),
    path('<slug:slug>/', views.tool_detail, name='detail'),
    path('<slug:slug>/process/', views.process_tool, name='process'),
]
