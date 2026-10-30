from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from decimal import Decimal

from .models import Product, Category, ProductImage
from .forms import ProductForm, CategoryForm
from vendors.models import Vendor
from accounts.decorators import vendor_required, admin_required


def product_list(request):
    """
    Marketplace Catalog View.
    Supports Search, Category, Price Range, Vendor filter, In-Stock filter, Sorting, and Pagination.
    Optimized with select_related.
    """
    products = Product.objects.filter(is_active=True, vendor__status='APPROVED').select_related('vendor', 'category')

    # Search Query (Q object)
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(vendor__store_name__icontains=query)
        )

    # Category Filter
    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Vendor Filter
    vendor_slug = request.GET.get('vendor', '').strip()
    if vendor_slug:
        products = products.filter(vendor__slug=vendor_slug)

    # Price Filter
    min_price = request.GET.get('min_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass

    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass

    # In-stock only filter
    in_stock = request.GET.get('in_stock', '').strip()
    if in_stock == '1':
        products = products.filter(stock__gt=0)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'featured':
        products = products.order_by('-featured', '-created_at')
    else:
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all categories and vendors for sidebar filters
    categories = Category.objects.filter(is_active=True).order_by('name')
    vendors = Vendor.objects.filter(status='APPROVED').order_by('store_name')

    context = {
        'products': page_obj,
        'categories': categories,
        'vendors': vendors,
        'query': query,
        'selected_category': category_slug,
        'selected_vendor': vendor_slug,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'selected_sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Product Detail View.
    Displays product info, gallery images, vendor shop card, stock status, and related products.
    """
    product = get_object_or_404(
        Product.objects.select_related('vendor', 'category').prefetch_related('gallery'),
        slug=slug,
        is_active=True
    )

    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        vendor__status='APPROVED'
    ).exclude(pk=product.pk).select_related('vendor')[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


# ==========================================
# Vendor-Specific Product Management (RBAC)
# ==========================================

@login_required
@vendor_required
def vendor_product_list(request):
    """Vendor view of all products belonging to their store."""
    vendor = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor).select_related('category').order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    elif status_filter == 'out_of_stock':
        products = products.filter(stock=0)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/vendor_product_list.html', {
        'products': page_obj,
        'status_filter': status_filter,
    })


@login_required
@vendor_required
def vendor_product_create(request):
    """Vendor adds a new product to their catalog."""
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()

            # Handle gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for img in gallery_images:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect('products:vendor_product_list')
    else:
        form = ProductForm()

    return render(request, 'products/vendor_product_form.html', {
        'form': form,
        'action': 'Create',
    })


@login_required
@vendor_required
def vendor_product_update(request, pk):
    """Vendor edits an existing product (Ownership validated)."""
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, pk=pk, vendor=vendor)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Handle additional gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for img in gallery_images:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('products:vendor_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/vendor_product_form.html', {
        'form': form,
        'product': product,
        'action': 'Update',
    })


@login_required
@vendor_required
def vendor_product_delete(request, pk):
    """Vendor deletes a product (Ownership validated)."""
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, pk=pk, vendor=vendor)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f"Product '{product_name}' was removed.")
        return redirect('products:vendor_product_list')

    return render(request, 'products/vendor_product_confirm_delete.html', {'product': product})


# ==========================================
# Admin Category Management (RBAC)
# ==========================================

@login_required
@admin_required
def admin_category_list(request):
    """Admin view to manage categories."""
    categories = Category.objects.all().order_by('name')
    return render(request, 'products/admin_category_list.html', {'categories': categories})


@login_required
@admin_required
def admin_category_create(request):
    """Admin creates a category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' created.")
            return redirect('products:admin_category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/admin_category_form.html', {'form': form, 'action': 'Create'})


@login_required
@admin_required
def admin_category_update(request, pk):
    """Admin edits a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect('products:admin_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'products/admin_category_form.html', {'form': form, 'category': category, 'action': 'Update'})


@login_required
@admin_required
def admin_category_delete(request, pk):
    """Admin deletes a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect('products:admin_category_list')
    return render(request, 'products/admin_category_confirm_delete.html', {'category': category})
