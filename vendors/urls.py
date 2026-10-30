from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
    path('profile/edit/', views.vendor_profile_edit, name='profile_edit'),
    path('store/<slug:slug>/', views.vendor_store_detail, name='vendor_store'),
    path('admin/approve/<int:vendor_id>/', views.admin_vendor_approve, name='admin_approve'),
    path('admin/reject/<int:vendor_id>/', views.admin_vendor_reject, name='admin_reject'),
]
