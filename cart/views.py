from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem


def _get_or_create_cart(request):
    """Retrieve or initialize shopping cart for authenticated or session user."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Check if an anonymous session cart exists and merge
        if request.session.session_key:
            session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def cart_detail(request):
    """View shopping cart details, calculate subtotals, and present checkout option."""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__vendor').all()
    subtotal = cart.get_total_amount()
    total = subtotal

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
    })


def cart_add(request, product_id):
    """Add a product to cart with requested quantity, checking stock."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        quantity = 1

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )

    new_quantity = cart_item.quantity + quantity
    if new_quantity > product.stock:
        messages.error(request, f"Sorry, only {product.stock} items are available in stock for '{product.name}'.")
        return redirect('products:product_detail', slug=product.slug)

    cart_item.quantity = new_quantity
    cart_item.save()

    messages.success(request, f"Added {quantity} x '{product.name}' to your cart.")
    return redirect('cart:detail')


def cart_update(request, item_id):
    """Update cart item quantity with stock validation."""
    if request.method == 'POST':
        cart = _get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)

        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity <= 0:
            item.delete()
            messages.info(request, f"Removed '{item.product.name}' from your cart.")
        elif quantity > item.product.stock:
            messages.error(request, f"Only {item.product.stock} units available in stock.")
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, f"Updated quantity for '{item.product.name}'.")

    return redirect('cart:detail')


def cart_remove(request, item_id):
    """Remove item from cart."""
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    name = item.product.name
    item.delete()
    messages.info(request, f"'{name}' was removed from your cart.")
    return redirect('cart:detail')


def cart_clear(request):
    """Clear all items from cart."""
    cart = _get_or_create_cart(request)
    cart.items.all().delete()
    messages.info(request, "Your shopping cart is now empty.")
    return redirect('cart:detail')
