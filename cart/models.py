from django.db import models
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_amount(self):
        return sum(item.subtotal for item in self.items.select_related('product'))

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key}"
        return f"Cart for {owner}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.product.get_selling_price() * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
