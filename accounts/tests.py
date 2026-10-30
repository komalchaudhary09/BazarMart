from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from vendors.models import Vendor

User = get_user_model()


class AuthenticationAndRBACTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='admin@test.com',
            password='password123',
            role='ADMIN'
        )
        self.vendor_user = User.objects.create_user(
            username='test_vendor',
            email='vendor@test.com',
            password='password123',
            role='VENDOR'
        )
        self.vendor_profile = Vendor.objects.create(
            user=self.vendor_user,
            store_name='Test Shop',
            status='APPROVED'
        )
        self.pending_vendor_user = User.objects.create_user(
            username='pending_vendor',
            email='pending@test.com',
            password='password123',
            role='VENDOR'
        )
        self.pending_vendor_profile = Vendor.objects.create(
            user=self.pending_vendor_user,
            store_name='Pending Shop',
            status='PENDING'
        )
        self.customer_user = User.objects.create_user(
            username='test_customer',
            email='customer@test.com',
            password='password123',
            role='CUSTOMER'
        )

    def test_customer_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_customer',
            'email': 'newcustomer@test.com',
            'first_name': 'New',
            'last_name': 'Customer',
            'password': 'StrongPassword@123',
            'confirm_password': 'StrongPassword@123',
            'phone': '9800000000',
            'address': 'Kathmandu'
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='new_customer')
        self.assertEqual(user.role, 'CUSTOMER')

    def test_vendor_registration_creates_pending_status(self):
        response = self.client.post(reverse('accounts:register_vendor'), {
            'username': 'applicant_vendor',
            'email': 'applicant@test.com',
            'first_name': 'Applicant',
            'last_name': 'Seller',
            'password': 'StrongPassword@123',
            'confirm_password': 'StrongPassword@123',
            'store_name': 'Applicant New Store',
            'store_description': 'Selling local goods',
            'store_address': 'Pokhara',
            'phone': '9811111111'
        })
        self.assertEqual(response.status_code, 302)
        vendor = Vendor.objects.get(store_name='Applicant New Store')
        self.assertEqual(vendor.status, 'PENDING')
        self.assertFalse(vendor.is_approved)

    def test_admin_dashboard_rbac(self):
        # Unauthenticated redirects to login
        response = self.client.get(reverse('dashboards:admin_dashboard'))
        self.assertEqual(response.status_code, 302)

        # Customer is denied access
        self.client.login(username='test_customer', password='password123')
        response = self.client.get(reverse('dashboards:admin_dashboard'))
        self.assertEqual(response.status_code, 302)

        # Admin gets 200 OK
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboards:admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_vendor_approval_workflow(self):
        self.client.login(username='test_admin', password='password123')
        # Approve the pending vendor
        response = self.client.get(reverse('vendors:admin_approve', kwargs={'vendor_id': self.pending_vendor_profile.pk}))
        self.assertEqual(response.status_code, 302)
        self.pending_vendor_profile.refresh_from_db()
        self.assertEqual(self.pending_vendor_profile.status, 'APPROVED')

    def test_login_page_renders_and_authenticates(self):
        # 1. Test clicking 'Sign In' (GET request to /accounts/login/) renders 200 OK
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
        self.assertContains(response, 'csrfmiddlewaretoken')

        # 2. Test successful customer login redirects to customer dashboard
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test_customer',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboards:dashboard_redirect'))

