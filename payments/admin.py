from django.contrib import admin
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_uuid', 'order', 'payment_method', 'amount', 'status', 'ref_id', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_uuid', 'ref_id', 'order__order_number')
    readonly_fields = ('order', 'transaction_uuid', 'payment_method', 'amount', 'ref_id', 'raw_response', 'created_at', 'updated_at')
