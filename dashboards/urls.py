from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/vendors/', views.admin_vendors, name='admin_vendors'),
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
]
