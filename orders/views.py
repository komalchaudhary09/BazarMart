from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator

from cart.views import _get_or_create_cart
from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from accounts.decorators import customer_required, vendor_required, admin_required


@login_required
def checkout_view(request):
    """
    Checkout process:
    Collects shipping and contact info, validates inventory stock,
    and dispatches to COD or eSewa payment gateway.
    """
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__vendor').all()

    if not cart_items.exists():
        messages.warning(request, "Your shopping cart is empty.")
        return redirect('products:product_list')

    # Stock validation
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Insufficient stock for '{item.product.name}'. Only {item.product.stock} available. Please update your cart."
            )
            return redirect('cart:detail')

    total_amount = cart.get_total_amount()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = total_amount
                order.save()

                # Create OrderItems linked to respective vendors
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        vendor=item.product.vendor,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.get_selling_price(),
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                        status='PENDING'
                    )

                if order.payment_method == 'COD':
                    # Deduct stock immediately for COD
                    for item in cart_items:
                        item.product.stock = max(0, item.product.stock - item.quantity)
                        item.product.save()

                    order.payment_status = 'PENDING'
                    order.order_status = 'PENDING'
                    order.save()

                    # Clear cart
                    cart.items.all().delete()
                    messages.success(request, f"Order {order.order_number} placed successfully via Cash on Delivery!")
                    return redirect('orders:order_success', order_number=order.order_number)

                elif order.payment_method == 'ESEWA':
                    # Forward to eSewa payment initiation
                    return redirect('payments:initiate_esewa', order_number=order.order_number)
    else:
        # Prepopulate customer contact info if available
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': request.user.phone or '',
            'shipping_address': request.user.address or '',
            'payment_method': 'COD'
        }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_amount': total_amount,
    })


@login_required
def order_success_view(request, order_number):
    """Order confirmation view with full summary."""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items', 'items__vendor'),
        order_number=order_number
    )
    if not (request.user == order.user or request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Unauthorized access to order details.")
        return redirect('dashboards:dashboard_redirect')

    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def customer_order_list(request):
    """Customer order history with status tracking."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders/customer_order_list.html', {
        'orders': page_obj,
        'selected_status': status_filter,
    })


@login_required
def customer_order_detail(request, order_number):
    """Customer order detail view."""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items', 'items__vendor', 'items__product'),
        order_number=order_number,
        user=request.user
    )
    return render(request, 'orders/customer_order_detail.html', {'order': order})


@login_required
def customer_order_invoice(request, order_number):
    """Printable invoice view."""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items', 'items__vendor'),
        order_number=order_number
    )
    if not (request.user == order.user or request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Unauthorized.")
        return redirect('dashboards:dashboard_redirect')

    return render(request, 'orders/invoice.html', {'order': order})


@login_required
def customer_order_cancel(request, order_number):
    """Customer can cancel pending orders, restoring product stock."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.order_status == 'PENDING':
        with transaction.atomic():
            order.order_status = 'CANCELLED'
            order.save()

            # Restore stock if COD or completed
            for item in order.items.select_related('product'):
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
                item.status = 'CANCELLED'
                item.save()

        messages.success(request, f"Order {order.order_number} has been cancelled.")
    else:
        messages.error(request, "This order cannot be cancelled as it is already being processed or delivered.")

    return redirect('orders:customer_order_detail', order_number=order.order_number)


# ==========================================
# Vendor Order Management (RBAC)
# ==========================================

@login_required
@vendor_required
def vendor_order_list(request):
    """Vendor view of order items containing products from their store."""
    vendor = request.user.vendor_profile
    order_items = OrderItem.objects.filter(vendor=vendor).select_related('order', 'product', 'order__user').order_by('-order__created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        order_items = order_items.filter(status=status_filter)

    paginator = Paginator(order_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders/vendor_order_list.html', {
        'order_items': page_obj,
        'selected_status': status_filter,
    })


@login_required
@vendor_required
def vendor_order_item_update(request, item_id):
    """Vendor updates the fulfillment status of an order item from their store."""
    vendor = request.user.vendor_profile
    item = get_object_or_404(OrderItem, pk=item_id, vendor=vendor)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in OrderItem.STATUS_CHOICES]
        if new_status in valid_statuses:
            item.status = new_status
            item.save()
            messages.success(request, f"Status for item '{item.product_name}' updated to {new_status}.")
        else:
            messages.error(request, "Invalid status choice.")

    return redirect('orders:vendor_order_list')


# ==========================================
# Admin Order Monitoring (RBAC)
# ==========================================

@login_required
@admin_required
def admin_order_list(request):
    """Admin monitors all orders across the marketplace."""
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    status = request.GET.get('status')
    if status:
        orders = orders.filter(order_status=status)

    payment_method = request.GET.get('payment_method')
    if payment_method:
        orders = orders.filter(payment_method=payment_method)

    payment_status = request.GET.get('payment_status')
    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders/admin_order_list.html', {
        'orders': page_obj,
        'selected_status': status,
        'selected_payment_method': payment_method,
        'selected_payment_status': payment_status,
    })


@login_required
@admin_required
def admin_order_detail(request, order_number):
    """Admin view of an order with ability to update global status."""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items', 'items__vendor', 'transactions'),
        order_number=order_number
    )

    if request.method == 'POST':
        new_order_status = request.POST.get('order_status')
        new_payment_status = request.POST.get('payment_status')

        if new_order_status:
            order.order_status = new_order_status
        if new_payment_status:
            order.payment_status = new_payment_status
        order.save()
        messages.success(request, f"Order {order.order_number} status updated successfully.")
        return redirect('orders:admin_order_detail', order_number=order.order_number)

    return render(request, 'orders/admin_order_detail.html', {'order': order})
