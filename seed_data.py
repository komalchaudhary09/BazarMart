import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multivendor_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from vendors.models import Vendor
from products.models import Category, Product
from orders.models import Order, OrderItem
from payments.models import PaymentTransaction

User = get_user_model()


def seed():
    print("Seeding database with multi-vendor marketplace initial data...")

    # 1. Superuser / Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@bazaarmart.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'phone': '+977-9801000001',
            'address': 'Durbar Marg, Kathmandu, Nepal'
        }
    )
    if created:
        admin_user.set_password('adminpassword123')
        admin_user.save()
        print("  Created Admin user: admin / adminpassword123")
    else:
        print("  Admin user already exists.")

    # 2. Vendor 1: Himalayan Tech Store (APPROVED)
    v1_user, created = User.objects.get_or_create(
        username='himalayan_tech',
        defaults={
            'email': 'contact@himalayantech.com',
            'first_name': 'Bikash',
            'last_name': 'Shrestha',
            'role': 'VENDOR',
            'phone': '+977-9841234567',
            'address': 'New Road, Kathmandu'
        }
    )
    if created:
        v1_user.set_password('vendorpassword123')
        v1_user.save()

    vendor_1, _ = Vendor.objects.get_or_create(
        user=v1_user,
        defaults={
            'store_name': 'Himalayan Tech Store',
            'description': 'Premier provider of high-grade electronics, laptop accessories, and audio gear in Kathmandu Valley.',
            'phone': '+977-9841234567',
            'address': 'Shop 42, New Road Supermarket, Kathmandu',
            'status': 'APPROVED',
            'commission_rate': Decimal('8.50')
        }
    )
    print("  Created Vendor 1: himalayan_tech / vendorpassword123 (APPROVED)")

    # 3. Vendor 2: Nepal Heritage & Crafts (APPROVED)
    v2_user, created = User.objects.get_or_create(
        username='nepali_crafts',
        defaults={
            'email': 'crafts@nepalheritage.org',
            'first_name': 'Sita',
            'last_name': 'Tamang',
            'role': 'VENDOR',
            'phone': '+977-9812345678',
            'address': 'Patan Durbar Square, Lalitpur'
        }
    )
    if created:
        v2_user.set_password('vendorpassword123')
        v2_user.save()

    vendor_2, _ = Vendor.objects.get_or_create(
        user=v2_user,
        defaults={
            'store_name': 'Nepal Heritage Crafts',
            'description': 'Handcrafted pashmina shawls, handmade Lokta paper journals, singing bowls, and authentic artisan crafts from local cooperatives.',
            'phone': '+977-9812345678',
            'address': 'Mangalbazar, Patan, Lalitpur',
            'status': 'APPROVED',
            'commission_rate': Decimal('10.00')
        }
    )
    print("  Created Vendor 2: nepali_crafts / vendorpassword123 (APPROVED)")

    # 4. Vendor 3: Everest Mountain Gear (PENDING - for testing approval workflow)
    v3_user, created = User.objects.get_or_create(
        username='everest_apparel',
        defaults={
            'email': 'info@everestgear.com',
            'first_name': 'Tenzing',
            'last_name': 'Sherpa',
            'role': 'VENDOR',
            'phone': '+977-9809876543',
            'address': 'Thamel, Kathmandu'
        }
    )
    if created:
        v3_user.set_password('vendorpassword123')
        v3_user.save()

    vendor_3, _ = Vendor.objects.get_or_create(
        user=v3_user,
        defaults={
            'store_name': 'Everest Mountain Gear',
            'description': 'High altitude trekking down jackets, sleeping bags, and outdoor expedition equipment.',
            'phone': '+977-9809876543',
            'address': 'Thamel Marg, Kathmandu',
            'status': 'PENDING',
            'commission_rate': Decimal('10.00')
        }
    )
    print("  Created Vendor 3: everest_apparel / vendorpassword123 (PENDING APPROVAL)")

    # 5. Customer: Ram Sharma
    customer_user, created = User.objects.get_or_create(
        username='ram_customer',
        defaults={
            'email': 'ram.sharma@example.com',
            'first_name': 'Ram',
            'last_name': 'Sharma',
            'role': 'CUSTOMER',
            'phone': '+977-9861112233',
            'address': 'Baneshwor, Ward 10, Kathmandu'
        }
    )
    if created:
        customer_user.set_password('customerpassword123')
        customer_user.save()
        print("  Created Customer: ram_customer / customerpassword123")
    else:
        print("  Customer ram_customer already exists.")

    # 6. Categories
    cat_electronics, _ = Category.objects.get_or_create(
        name='Electronics & Gadgets',
        defaults={'description': 'Headphones, computer accessories, smart devices, and chargers.'}
    )
    cat_crafts, _ = Category.objects.get_or_create(
        name='Handicrafts & Art',
        defaults={'description': 'Authentic traditional Nepali artisan decor and meditation tools.'}
    )
    cat_apparel, _ = Category.objects.get_or_create(
        name='Clothing & Pashmina',
        defaults={'description': 'Pure cashmere, wool scarves, pashmina stoles, and clothing.'}
    )
    cat_outdoors, _ = Category.objects.get_or_create(
        name='Trekking & Outdoors',
        defaults={'description': 'Backpacks, trekking poles, jackets, and camping accessories.'}
    )

    # 7. Products
    products_data = [
        {
            'vendor': vendor_1,
            'category': cat_electronics,
            'name': 'Wireless Noise Cancelling Earbuds Pro',
            'description': 'Premium active noise cancellation earbuds with Bluetooth 5.3, 36-hour total battery life with wireless charging case, and IPX5 water resistance for workouts and monsoon rains.',
            'price': Decimal('4500.00'),
            'discount_price': Decimal('3800.00'),
            'stock': 25,
            'is_active': True,
            'featured': True,
        },
        {
            'vendor': vendor_1,
            'category': cat_electronics,
            'name': 'Mechanical Gaming Keyboard RGB (Brown Switch)',
            'description': 'Hot-swappable mechanical switches with tactile feedback, aluminum frame, customizable per-key RGB backlighting, and braided USB-C detachable cable.',
            'price': Decimal('6200.00'),
            'discount_price': Decimal('5500.00'),
            'stock': 12,
            'is_active': True,
            'featured': True,
        },
        {
            'vendor': vendor_1,
            'category': cat_electronics,
            'name': 'Ultra-Fast 65W GaN Fast Charger',
            'description': 'Compact dual USB-C and USB-A charging brick capable of powering MacBook Pro, Dell XPS, iPhone, and Android smartphones simultaneously with intelligent power delivery.',
            'price': Decimal('2800.00'),
            'discount_price': None,
            'stock': 40,
            'is_active': True,
            'featured': False,
        },
        {
            'vendor': vendor_2,
            'category': cat_apparel,
            'name': 'Authentic Pure Himalayan Cashmere Pashmina Stole',
            'description': '100% genuine Chyangra cashmere hand-spun and handwoven on traditional wooden looms in Lalitpur. Incredibly soft, featherlight warmth with hand-twisted fringes.',
            'price': Decimal('8500.00'),
            'discount_price': Decimal('7200.00'),
            'stock': 8,
            'is_active': True,
            'featured': True,
        },
        {
            'vendor': vendor_2,
            'category': cat_crafts,
            'name': 'Hand-Hammered 7 Metals Tibetan Singing Bowl Set',
            'description': 'Master artisan hand-hammered singing bowl crafted from alloy of seven planetary metals. Emits rich, sustained harmonic resonant frequencies for sound therapy and mindfulness meditation. Includes leather mallet and silk cushion.',
            'price': Decimal('4200.00'),
            'discount_price': Decimal('3600.00'),
            'stock': 15,
            'is_active': True,
            'featured': True,
        },
        {
            'vendor': vendor_2,
            'category': cat_crafts,
            'name': 'Handmade Lokta Paper Leather Bound Journal',
            'description': 'Eco-friendly traditional wild Daphne bark paper bound in genuine buffalo leather. Acid-free, termite-resistant paper that lasts for centuries without yellowing.',
            'price': Decimal('1200.00'),
            'discount_price': Decimal('950.00'),
            'stock': 30,
            'is_active': True,
            'featured': False,
        },
        {
            'vendor': vendor_1,
            'category': cat_electronics,
            'name': 'Portable 20,000mAh Heavy Duty Power Bank',
            'description': '22.5W quick charge battery pack with LED percentage display and multi-port safety circuit. Ideal for multi-day trekking in Annapurna or Everest regions.',
            'price': Decimal('3200.00'),
            'discount_price': Decimal('2850.00'),
            'stock': 3,  # Low stock test
            'is_active': True,
            'featured': False,
        },
    ]

    for pdata in products_data:
        p, created = Product.objects.get_or_create(
            vendor=pdata['vendor'],
            name=pdata['name'],
            defaults=pdata
        )
        if created:
            print(f"  Created product: {p.name}")

    # 8. Sample Order for Ram Customer
    p1 = Product.objects.get(name='Wireless Noise Cancelling Earbuds Pro')
    p2 = Product.objects.get(name='Handmade Lokta Paper Leather Bound Journal')

    sample_order, order_created = Order.objects.get_or_create(
        user=customer_user,
        full_name='Ram Sharma',
        defaults={
            'email': 'ram.sharma@example.com',
            'phone': '+977-9861112233',
            'shipping_address': 'House 14, Ward 10, New Baneshwor',
            'city': 'Kathmandu',
            'postal_code': '44600',
            'total_amount': Decimal('4750.00'),
            'payment_method': 'ESEWA',
            'payment_status': 'COMPLETED',
            'order_status': 'PROCESSING',
            'notes': 'Please call before delivery.'
        }
    )

    if order_created:
        OrderItem.objects.create(
            order=sample_order,
            vendor=p1.vendor,
            product=p1,
            product_name=p1.name,
            price=p1.get_selling_price(),
            quantity=1,
            subtotal=p1.get_selling_price(),
            status='PROCESSING'
        )
        OrderItem.objects.create(
            order=sample_order,
            vendor=p2.vendor,
            product=p2,
            product_name=p2.name,
            price=p2.get_selling_price(),
            quantity=1,
            subtotal=p2.get_selling_price(),
            status='PENDING'
        )
        PaymentTransaction.objects.create(
            order=sample_order,
            transaction_uuid=f"{sample_order.order_number}-1718000000",
            payment_method='ESEWA',
            amount=sample_order.total_amount,
            status='SUCCESS',
            ref_id='00045XZQ'
        )
        print(f"  Created sample verified order: {sample_order.order_number}")

    print("\nDatabase seeded successfully!")


if __name__ == '__main__':
    seed()
