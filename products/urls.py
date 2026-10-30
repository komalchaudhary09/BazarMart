from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Marketplace public browsing
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Vendor-specific product management
    path('vendor/products/', views.vendor_product_list, name='vendor_product_list'),
    path('vendor/products/add/', views.vendor_product_create, name='vendor_product_create'),
    path('vendor/products/<int:pk>/edit/', views.vendor_product_update, name='vendor_product_update'),
    path('vendor/products/<int:pk>/delete/', views.vendor_product_delete, name='vendor_product_delete'),

    # Admin Category management
    path('admin/categories/', views.admin_category_list, name='admin_category_list'),
    path('admin/categories/add/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:pk>/edit/', views.admin_category_update, name='admin_category_update'),
    path('admin/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),
]
