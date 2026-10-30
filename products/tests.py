from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from products.models import Category, Product

User = get_user_model()


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vendor_user = User.objects.create_user(
            username='seller1', email='seller1@test.com', password='password123', role='VENDOR'
        )
        self.vendor = Vendor.objects.create(
            user=self.vendor_user, store_name='Gadget Central', status='APPROVED'
        )
        self.category = Category.objects.create(name='Electronics', description='Tech gear')

        self.product = Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name='Bluetooth Speaker',
            description='Clear sound speaker',
            price=Decimal('2000.00'),
            discount_price=Decimal('1800.00'),
            stock=10,
            is_active=True
        )

    def test_product_selling_price_and_discount(self):
        self.assertEqual(self.product.get_selling_price(), Decimal('1800.00'))
        self.assertEqual(self.product.discount_percentage, 10)
        self.assertTrue(self.product.is_in_stock)

    def test_product_list_view_and_search(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bluetooth Speaker')

        # Test search
        search_res = self.client.get(reverse('products:product_list') + '?q=Bluetooth')
        self.assertContains(search_res, 'Bluetooth Speaker')

        # Test filter by category
        cat_res = self.client.get(reverse('products:product_list') + f'?category={self.category.slug}')
        self.assertContains(cat_res, 'Bluetooth Speaker')

    def test_product_detail_view(self):
        response = self.client.get(reverse('products:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gadget Central')
        self.assertContains(response, 'NPR 1800.00')
