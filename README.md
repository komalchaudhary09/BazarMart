# BazaarMart — Multi-Vendor E-Commerce Marketplace

A full-featured, production-ready Multi-Vendor Marketplace built with **Python 3.12**, **Django 6**, and **Tailwind CSS**. The platform provides role-based access control for **Admins**, **Vendors**, and **Customers**, vendor shop management, stock tracking, and payment gateways: **Cash on Delivery (COD)** and **eSewa ePay v2** (with official HMAC-SHA256 signature verification).

---

## 🌟 Key Features

### 1. User Roles & Role-Based Access Control (RBAC)
- **Admin**: Superuser control center, vendor approval/rejection workflow, catalog category management, global order monitoring, revenue analytics.
- **Vendor**: Merchant storefront, shop branding (logo, banner, bio), vendor-specific product CRUD, inventory stock monitoring, order fulfillment for shop items.
- **Customer**: Buyer account, cart management, checkout with COD and eSewa, order tracking, downloadable/printable tax invoices, profile management.
- **Security**: Granular custom decorators (`@admin_required`, `@vendor_required`, `@customer_required`, `@role_required`), ownership verification on all resource edits, CSRF protection, and secure forms.

### 2. Vendor Management & Approval Workflow
- Vendor registration with store name, description, address, and logo.
- Automatic **`PENDING`** approval status upon vendor registration.
- Admin review dashboard to inspect merchant details and **Approve** or **Reject** with custom feedback.
- Unapproved vendors see an informative holding dashboard; only approved vendors can list products.
- Dedicated public vendor storefronts (`/vendors/store/<slug>/`) displaying vendor branding, contact info, and their active catalog.

### 3. Product Catalog & Inventory
- Category management with slugs and navigation integration.
- Vendor-isolated product CRUD with multi-image gallery upload (`ProductImage`).
- Dynamic pricing with discount percentage calculation and selling price helpers.
- Automated inventory deduction upon order placement; out-of-stock indicators prevent overselling.

### 4. Marketplace Features
- **Search**: Keyword search across titles, descriptions, categories, and merchant names.
- **Filtering**: By Category, Vendor, Price Range (Min/Max), and In-Stock items only.
- **Sorting**: Newest arrivals, Price (Low to High), Price (High to Low), Name (A-Z).
- **Pagination**: 12 items per page with preserved query parameters across page switches.
- **Performance**: Optimized ORM queries using `select_related` and `prefetch_related`.

### 5. Shopping Cart
- Database-backed cart supporting both authenticated users and anonymous guest sessions.
- Seamless automatic merging of session cart into user cart upon login.
- Dynamic item quantity adjustment, stock boundary checking, removal, and live navbar badges.

### 6. Checkout & Payment Gateways
- **Cash on Delivery (COD)**: Instant order confirmation with immediate stock deduction.
- **eSewa (ePay v2)**: Official implementation compliant with eSewa's latest documentation:
  - Form POST to `https://rc-epay.esewa.com.np/api/epay/main/v2/form`
  - Automated HMAC-SHA256 signature calculation using Merchant Secret Key
  - Return callback handler: decodes base64 payload, validates signature, verifies status via eSewa transaction status API
  - Automatically updates `Order` payment status to `COMPLETED` and logs `PaymentTransaction` with reference ID.

### 7. Dashboards
- **Admin Dashboard**: Gross sales volume, order counts, active/pending vendor counts, low stock alerts, quick approval queue.
- **Vendor Dashboard**: Shop revenue, units sold, product count, stock warnings, and fulfillment orders table.
- **Customer Dashboard**: Purchase history, active order tracking, total spend, and profile shortcut.

---

## 🔑 Pre-Seeded Demo Accounts

You can test all three roles immediately after seeding:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `adminpassword123` | Platform Superuser & Admin Dashboard |
| **Approved Vendor** | `himalayan_tech` | `vendorpassword123` | Himalayan Tech Store (Electronics) |
| **Approved Vendor** | `nepali_crafts` | `vendorpassword123` | Nepal Heritage Crafts (Pashmina & Art) |
| **Pending Vendor** | `everest_apparel` | `vendorpassword123` | Awaiting approval (test approval workflow) |
| **Customer** | `ram_customer` | `customerpassword123` | Has 1 pre-filled order with invoice |

---

## 💳 eSewa Payment Integration Details

The project implements the official **eSewa ePay v2** protocol:

- **Endpoint (Test Sandbox)**: `https://rc-epay.esewa.com.np/api/epay/main/v2/form`
- **Product Code (Merchant ID)**: `EPAYTEST`
- **Secret Key**: `8gBm/:&EnhH.1/q`
- **Signature Message**:
  ```text
  total_amount={amount},transaction_uuid={uuid},product_code={product_code}
  ```
- **Hash Algorithm**: `HMAC-SHA256` encoded in Base64.
- **Return URL**: Handles base64 encoded JSON returned from eSewa, validates signature, checks server status verification API, marks order paid, and deducts inventory.

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=django-insecure-m0!8d%ksnkx$@!m-z4w(6vm)ea)4&%9_o!m=k5-$muxnicueh%
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

# eSewa Configuration (Sandbox)
ESEWA_PRODUCT_CODE=EPAYTEST
ESEWA_SECRET_KEY=8gBm/:&EnhH.1/q
ESEWA_PAYMENT_URL=https://rc-epay.esewa.com.np/api/epay/main/v2/form
ESEWA_STATUS_CHECK_URL=https://rc-epay.esewa.com.np/api/epay/transaction/status/
```

---

## 🚀 Quick Start & Local Setup

### 1. Clone & Enter Project
```bash
git clone <repository-url>
cd <project-folder>
```

### 2. Create and Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Initial Data (Admin, Vendors, Products, Orders)
```bash
python seed_data.py
```

### 6. Collect Static Assets
```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## 🧪 Running Automated Tests

Run the test suite verifying authentication, RBAC, cart stock controls, and eSewa signatures:

```bash
python manage.py test
```

---

## 🌐 Public Production Deployment Guide

### Option 1: Render.com (Recommended Free/PaaS Deployment)
1. Push this repository to GitHub or GitLab.
2. In [Render Dashboard](https://dashboard.render.com/), click **New +** > **Web Service**.
3. Select your repository.
4. Configure:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && python seed_data.py`
   - **Start Command**: `gunicorn multivendor_core.wsgi:application`
5. Add Environment Variables under **Settings > Environment**:
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<Generate a random secure key>`
   - `ALLOWED_HOSTS`: `.onrender.com,yourcustomdomain.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`
   - `ESEWA_PRODUCT_CODE`: `EPAYTEST`
   - `ESEWA_SECRET_KEY`: `8gBm/:&EnhH.1/q`

### Option 2: Railway.app
1. Link your GitHub repo to Railway.
2. Railway detects the `Procfile` and `requirements.txt` automatically.
3. In variables, configure `SECRET_KEY`, `ALLOWED_HOSTS=*`, and `DEBUG=False`.
4. Deploy with one click.

### Option 3: Docker Deployment
Build and run the containerized application locally or on any cloud VPS (DigitalOcean, AWS EC2, Linode):

```bash
docker build -t bazaarmart .
docker run -p 8000:8000 --env-file .env bazaarmart
```

Or using Docker Compose:
```bash
docker-compose up --build -d
```

---

## 📁 Project Architecture & App Structure

```text
├── accounts/          # Custom User model (ADMIN, VENDOR, CUSTOMER), RBAC decorators, profiles
├── vendors/           # Vendor storefronts, approval workflow, store customization
├── products/          # Categories, Product CRUD, image gallery, inventory & discounts
├── cart/              # Session-aware shopping cart with quantity controls & subtotals
├── orders/            # Checkout, Order/OrderItem models, customer tracking, printable invoice
├── payments/          # eSewa ePay v2 integration (HMAC-SHA256 signature, callbacks), COD
├── dashboards/        # Role-specific dashboards (Admin, Vendor, Customer)
├── multivendor_core/  # Root settings, URLs routing, WSGI/ASGI configurations
├── templates/         # Clean, responsive Tailwind CSS layouts & views
├── static/            # Static assets
├── media/             # Uploaded product photos, vendor logos, user avatars
├── seed_data.py       # Instant database seeder with pre-configured accounts
├── requirements.txt   # Frozen production dependencies
├── Dockerfile         # Container specification
├── Procfile           # Production WSGI process runner
└── README.md          # Comprehensive documentation
```
