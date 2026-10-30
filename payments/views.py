import time
import logging
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.db import transaction

from orders.models import Order
from cart.models import Cart
from .models import PaymentTransaction
from .services import generate_esewa_signature, decode_esewa_response, verify_esewa_transaction

logger = logging.getLogger(__name__)


def initiate_esewa(request, order_number):
    """
    Initiate eSewa v2 online checkout payment.
    Prepares payload and HMAC signature, then renders auto-submitting form.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.payment_status == 'COMPLETED':
        messages.info(request, "This order has already been paid for.")
        return redirect('orders:order_success', order_number=order.order_number)

    # Clean amount formatting for eSewa (e.g. 100 or 100.50)
    total_amount_str = f"{order.total_amount:.2f}".rstrip('0').rstrip('.') if '.' in f"{order.total_amount:.2f}" else f"{order.total_amount}"
    # eSewa requirement: integer amount if decimal part is 0, e.g. "100"
    if Decimal(total_amount_str) == int(order.total_amount):
        total_amount_str = str(int(order.total_amount))

    transaction_uuid = f"{order.order_number}-{int(time.time())}"
    product_code = getattr(settings, 'ESEWA_PRODUCT_CODE', 'EPAYTEST')
    secret_key = getattr(settings, 'ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
    payment_url = getattr(settings, 'ESEWA_PAYMENT_URL', 'https://rc-epay.esewa.com.np/api/epay/main/v2/form')

    signature = generate_esewa_signature(
        total_amount=total_amount_str,
        transaction_uuid=transaction_uuid,
        product_code=product_code,
        secret_key=secret_key
    )

    # Record pending transaction
    PaymentTransaction.objects.create(
        order=order,
        transaction_uuid=transaction_uuid,
        payment_method='ESEWA',
        amount=order.total_amount,
        status='PENDING'
    )

    success_url = request.build_absolute_uri(reverse('payments:esewa_success'))
    failure_url = request.build_absolute_uri(reverse('payments:esewa_failure'))

    context = {
        'payment_url': payment_url,
        'amount': total_amount_str,
        'tax_amount': '0',
        'total_amount': total_amount_str,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': success_url,
        'failure_url': failure_url,
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
        'order': order,
    }

    return render(request, 'payments/esewa_redirect.html', context)


def esewa_success(request):
    """
    Handle return redirect from eSewa upon successful payment.
    Decodes base64 payload, verifies signature/status, deducts stock, and marks order paid.
    """
    encoded_data = request.GET.get('data')
    if not encoded_data:
        messages.error(request, "No transaction data received from eSewa.")
        return redirect('products:product_list')

    data = decode_esewa_response(encoded_data)
    if not data:
        messages.error(request, "Failed to decode eSewa response payload.")
        return redirect('products:product_list')

    transaction_uuid = data.get('transaction_uuid')
    transaction_code = data.get('transaction_code')
    status = data.get('status')
    total_amount = data.get('total_amount')
    product_code = data.get('product_code', getattr(settings, 'ESEWA_PRODUCT_CODE', 'EPAYTEST'))

    payment_record = PaymentTransaction.objects.filter(transaction_uuid=transaction_uuid).first()
    if not payment_record:
        messages.error(request, "Payment transaction record not found.")
        return redirect('products:product_list')

    order = payment_record.order

    # Optional server status check API verification
    server_verified = False
    verification_data = verify_esewa_transaction(product_code, total_amount, transaction_uuid)
    if verification_data and verification_data.get('status') == 'COMPLETE':
        server_verified = True

    if status == 'COMPLETE' or server_verified:
        with transaction.atomic():
            # Update transaction record
            payment_record.status = 'SUCCESS'
            payment_record.ref_id = transaction_code
            payment_record.raw_response = data
            payment_record.save()

            # Update Order
            order.payment_status = 'COMPLETED'
            order.order_status = 'PROCESSING'
            order.save()

            # Deduct stock for all items
            for item in order.items.select_related('product'):
                if item.product:
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

            # Clear cart for user
            if order.user:
                Cart.objects.filter(user=order.user).delete()
            if request.session.session_key:
                Cart.objects.filter(session_key=request.session.session_key).delete()

        messages.success(
            request,
            f"eSewa payment of NPR {order.total_amount} was verified successfully! Reference ID: {transaction_code}"
        )
        return redirect('orders:order_success', order_number=order.order_number)
    else:
        payment_record.status = 'FAILED'
        payment_record.raw_response = data
        payment_record.save()
        messages.error(request, f"eSewa payment verification failed. Status: {status}")
        return redirect('payments:esewa_failure')


def esewa_failure(request):
    """
    Handle return redirect from eSewa when payment is canceled or fails.
    """
    return render(request, 'payments/esewa_failure.html')
