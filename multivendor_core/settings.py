import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-m0!8d%ksnkx$@!m-z4w(6vm)ea)4&%9_o!m=k5-$muxnicueh%')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

allowed_hosts_str = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_str.split(',') if h.strip()]

csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1,http://localhost')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins.split(',') if o.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Custom Core Apps
    'accounts.apps.AccountsConfig',
    'vendors.apps.VendorsConfig',
    'products.apps.ProductsConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'payments.apps.PaymentsConfig',
    'dashboards.apps.DashboardsConfig',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'multivendor_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_summary',
                'products.context_processors.categories_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'multivendor_core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboards:dashboard_redirect'
LOGOUT_REDIRECT_URL = 'products:product_list'

# eSewa Payment Settings
ESEWA_PRODUCT_CODE = os.getenv('ESEWA_PRODUCT_CODE', 'EPAYTEST')
ESEWA_SECRET_KEY = os.getenv('ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
ESEWA_PAYMENT_URL = os.getenv('ESEWA_PAYMENT_URL', 'https://rc-epay.esewa.com.np/api/epay/main/v2/form')
ESEWA_STATUS_CHECK_URL = os.getenv('ESEWA_STATUS_CHECK_URL', 'https://rc-epay.esewa.com.np/api/epay/transaction/status/')

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
