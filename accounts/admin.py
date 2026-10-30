from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Info', {'fields': ('role', 'phone', 'address', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Info', {'fields': ('role', 'phone', 'address', 'avatar')}),
    )
