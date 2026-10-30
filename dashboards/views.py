from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from decimal import Decimal

from accounts.models import User
from vendors.models import Vendor
from products.models import Product, Category
from orders.models import Order, OrderItem
from accounts.decorators import admin_required, vendor_required, customer_required


@login_required
def dashboard_redirect(request):
    """Dispatches the user to their appropriate role-based dashboard."""
    if request.user.is_superuser or request.user.role == 'ADMIN':
        return redirect('dashboards:admin_dashboard')
    elif request.user.role == 'VENDOR':
        return redirect('dashboards:vendor_dashboard')
    else:
        return redirect('dashboards:customer_dashboard')


@login_required
@admin_required
def admin_dashboard(request):
    """
    Comprehensive Admin Dashboard:
    High-level platform statistics, revenue, order tracking, vendor approvals, and low stock warnings.
    """
    total_sales = Order.objects.filter(payment_status='COMPLETED').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_orders = Order.objects.count()
    total_vendors = Vendor.objects.filter(status='APPROVED').count()
    pending_vendors = Vendor.objects.filter(status='PENDING').count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(role='CUSTOMER').count()

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]

    # Pending vendors needing review
    pending_vendor_list = Vendor.objects.filter(status='PENDING').select_related('user').order_by('-created_at')[:5]

    # Low stock alerts (<= 5 units)
    low_stock_products = Product.objects.filter(stock__lte=5).select_related('vendor', 'category')[:6]

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_vendors': total_vendors,
        'pending_vendors': pending_vendors,
        'total_products': total_products,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'pending_vendor_list': pending_vendor_list,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
@admin_required
def admin_vendors(request):
    """Admin view to manage and filter all marketplace vendors."""
    status_filter = request.GET.get('status')
    vendors = Vendor.objects.select_related('user').annotate(product_count=Count('products')).order_by('-created_at')

    if status_filter:
        vendors = vendors.filter(status=status_filter)

    return render(request, 'dashboards/admin_vendors.html', {
        'vendors': vendors,
        'selected_status': status_filter,
    })


@login_required
def vendor_dashboard(request):
    """
    Vendor Dashboard:
    Store sales performance, product counts, stock status, and fulfillment orders.
    Shows pending state banner if vendor account is not yet approved by admin.
    """
    if not (request.user.role == 'VENDOR' or request.user.is_superuser):
        messages.error(request, "Access restricted to vendor accounts.")
        return redirect('dashboards:dashboard_redirect')

    vendor = getattr(request.user, 'vendor_profile', None)
    if not vendor:
        messages.error(request, "No vendor profile associated with your user account.")
        return redirect('products:product_list')

    # If pending or rejected, render state dashboard with information
    if vendor.status != 'APPROVED':
        return render(request, 'dashboards/vendor_pending.html', {'vendor': vendor})

    # Approved Vendor metrics
    vendor_items = OrderItem.objects.filter(vendor=vendor)
    total_sales = vendor_items.filter(order__payment_status='COMPLETED').aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    total_sold_units = vendor_items.filter(order__payment_status='COMPLETED').aggregate(total=Sum('quantity'))['total'] or 0
    total_products = Product.objects.filter(vendor=vendor).count()
    low_stock_count = Product.objects.filter(vendor=vendor, stock__lte=5).count()

    # Recent order items
    recent_items = vendor_items.select_related('order', 'product', 'order__user').order_by('-order__created_at')[:8]

    # Low stock list
    low_stock_products = Product.objects.filter(vendor=vendor, stock__lte=5).order_by('stock')[:5]

    context = {
        'vendor': vendor,
        'total_sales': total_sales,
        'total_sold_units': total_sold_units,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'recent_items': recent_items,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboards/vendor_dashboard.html', context)


@login_required
def customer_dashboard(request):
    """
    Customer Dashboard:
    Order summaries, delivery tracking shortcuts, recent purchases, and profile overview.
    """
    customer_orders = Order.objects.filter(user=request.user)
    total_orders = customer_orders.count()
    pending_orders = customer_orders.filter(order_status__in=['PENDING', 'PROCESSING', 'SHIPPED']).count()
    completed_orders = customer_orders.filter(order_status='DELIVERED').count()
    total_spent = customer_orders.filter(payment_status='COMPLETED').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    recent_orders = customer_orders.prefetch_related('items').order_by('-created_at')[:6]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboards/customer_dashboard.html', context)
