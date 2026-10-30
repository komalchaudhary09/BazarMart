from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'phone', 'status', 'commission_rate', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('store_name', 'user__username', 'user__email', 'phone')
    prepopulated_fields = {'slug': ('store_name',)}
    actions = ['approve_vendors', 'reject_vendors']

    def approve_vendors(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, f"{queryset.count()} vendors approved successfully.")
    approve_vendors.short_description = "Approve selected vendors"

    def reject_vendors(self, request, queryset):
        queryset.update(status='REJECTED')
        self.message_user(request, f"{queryset.count()} vendors rejected.")
    reject_vendors.short_description = "Reject selected vendors"
