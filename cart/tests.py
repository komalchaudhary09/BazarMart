from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from products.models import Category, Product
from cart.models import Cart, CartItem

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vendor_user = User.objects.create_user(username='v1', password='password123', role='VENDOR')
        self.vendor = Vendor.objects.create(user=self.vendor_user, store_name='Store A', status='APPROVED')
        self.category = Category.objects.create(name='Gadgets')
        self.product = Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name='USB Cable',
            description='Type-C cable',
            price=Decimal('500.00'),
            stock=5,
            is_active=True
        )

    def test_add_to_cart_and_update(self):
        # Add to cart
        response = self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}), {'quantity': 2})
        self.assertEqual(response.status_code, 302)

        # Check cart detail page
        response = self.client.get(reverse('cart:detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'USB Cable')
        self.assertContains(response, 'NPR 1000.00')

        # Exceeding stock check
        response = self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}), {'quantity': 10})
        self.assertEqual(response.status_code, 302)
        # Should not exceed available stock 5
        cart = Cart.objects.first()
        item = cart.items.first()
        self.assertLessEqual(item.quantity, 5)
