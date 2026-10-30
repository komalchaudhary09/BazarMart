from django.db import models
from orders.models import Order


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_uuid = models.CharField(max_length=100, unique=True, db_index=True)
    payment_method = models.CharField(max_length=20, choices=Order.PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.payment_method} - {self.transaction_uuid} ({self.status})"
