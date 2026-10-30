from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'discount_price', 'stock', 'is_active', 'featured')
    list_filter = ('is_active', 'featured', 'category', 'vendor')
    search_fields = ('name', 'description', 'vendor__store_name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
