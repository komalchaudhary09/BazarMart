from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
import base64
import json
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from products.models import Product
from orders.models import Order, OrderItem
from payments.services import generate_esewa_signature, decode_esewa_response

User = get_user_model()


class PaymentAndEsewaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buyer', password='password123', role='CUSTOMER')
        self.vendor_user = User.objects.create_user(username='seller', password='password123', role='VENDOR')
        self.vendor = Vendor.objects.create(user=self.vendor_user, store_name='Shop X', status='APPROVED')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Item',
            description='Test',
            price=Decimal('100.00'),
            stock=10,
            is_active=True
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name='Buyer Name',
            email='buyer@test.com',
            phone='9800000000',
            shipping_address='Street 1',
            city='Kathmandu',
            total_amount=Decimal('100.00'),
            payment_method='ESEWA',
            payment_status='PENDING'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            vendor=self.vendor,
            product=self.product,
            product_name=self.product.name,
            price=self.product.price,
            quantity=1,
            subtotal=self.product.price
        )

    def test_esewa_signature_generation(self):
        total_amount = '100'
        transaction_uuid = '240812-123456'
        product_code = 'EPAYTEST'
        secret_key = '8gBm/:&EnhH.1/q'

        signature = generate_esewa_signature(total_amount, transaction_uuid, product_code, secret_key)
        self.assertTrue(bool(signature))
        self.assertIsInstance(signature, str)

        # Generating again with same parameters produces deterministic signature
        signature2 = generate_esewa_signature(total_amount, transaction_uuid, product_code, secret_key)
        self.assertEqual(signature, signature2)

    def test_esewa_response_decoding(self):
        payload = {
            "transaction_code": "000TEST",
            "status": "COMPLETE",
            "total_amount": "100.0",
            "transaction_uuid": "ORD-123",
            "product_code": "EPAYTEST"
        }
        encoded = base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
        decoded = decode_esewa_response(encoded)
        self.assertEqual(decoded['transaction_code'], "000TEST")
        self.assertEqual(decoded['status'], "COMPLETE")

    def test_initiate_esewa_view(self):
        self.client.login(username='buyer', password='password123')
        response = self.client.get(reverse('payments:initiate_esewa', kwargs={'order_number': self.order.order_number}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EPAYTEST')
        self.assertContains(response, 'signature')
        self.assertContains(response, 'rc-epay.esewa.com.np')
