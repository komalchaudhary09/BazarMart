from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Vendor(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    store_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='vendor_banners/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    rejection_reason = models.TextField(blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.store_name)
            slug = base_slug
            counter = 1
            while Vendor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_approved(self):
        return self.status == 'APPROVED'

    def __str__(self):
        return f"{self.store_name} ({self.get_status_display()})"
