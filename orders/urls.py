from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.customer_order_list, name='customer_order_list'),
    path('my-orders/<str:order_number>/', views.customer_order_detail, name='customer_order_detail'),
    path('my-orders/<str:order_number>/invoice/', views.customer_order_invoice, name='customer_order_invoice'),
    path('my-orders/<str:order_number>/cancel/', views.customer_order_cancel, name='customer_order_cancel'),

    # Vendor Fulfillment
    path('vendor/orders/', views.vendor_order_list, name='vendor_order_list'),
    path('vendor/orders/item/<int:item_id>/update/', views.vendor_order_item_update, name='vendor_order_item_update'),

    # Admin Monitoring
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<str:order_number>/', views.admin_order_detail, name='admin_order_detail'),
]
