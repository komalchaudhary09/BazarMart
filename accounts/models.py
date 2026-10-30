from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('VENDOR', 'Vendor'),
        ('CUSTOMER', 'Customer'),
    )

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CUSTOMER', db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    objects = UserManager()

    @property
    def is_admin_role(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_vendor_role(self):
        return self.role == 'VENDOR'

    @property
    def is_customer_role(self):
        return self.role == 'CUSTOMER'

    @property
    def is_approved_vendor(self):
        if not self.is_vendor_role:
            return False
        return hasattr(self, 'vendor_profile') and self.vendor_profile.status == 'APPROVED'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
