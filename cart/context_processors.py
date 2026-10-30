from .models import Cart


def cart_summary(request):
    """
    Context processor to provide cart item count and subtotal to all templates.
    """
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if cart:
        total_items = cart.get_total_items()
        total_price = cart.get_total_amount()
    else:
        total_items = 0
        total_price = 0

    return {
        'cart_item_count': total_items,
        'cart_total_price': total_price,
    }
