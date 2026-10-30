from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Vendor
from .forms import VendorProfileForm
from accounts.decorators import admin_required, vendor_required


def vendor_list(request):
    """Public list of approved marketplace vendors."""
    vendors = Vendor.objects.filter(status='APPROVED').annotate(
        product_count=Count('products')
    ).order_by('store_name')
    return render(request, 'vendors/vendor_list.html', {'vendors': vendors})


def vendor_store_detail(request, slug):
    """Public vendor shop profile displaying store information and products."""
    vendor = get_object_or_404(Vendor, slug=slug, status='APPROVED')
    products = vendor.products.filter(is_active=True).select_related('category')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'vendors/vendor_store.html', {
        'vendor': vendor,
        'products': page_obj,
        'selected_category': category_slug,
        'selected_sort': sort,
    })


@login_required
@vendor_required
def vendor_profile_edit(request):
    """Vendor can manage shop details, logo, banner."""
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Your shop profile has been updated successfully!")
            return redirect('vendors:profile_edit')
    else:
        form = VendorProfileForm(instance=vendor)

    return render(request, 'vendors/vendor_profile_edit.html', {'form': form, 'vendor': vendor})


@login_required
@admin_required
def admin_vendor_approve(request, vendor_id):
    """Admin action to approve vendor application."""
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    vendor.status = 'APPROVED'
    vendor.rejection_reason = ''
    vendor.save()
    messages.success(request, f"Vendor '{vendor.store_name}' approved successfully!")
    return redirect('dashboards:admin_vendors')


@login_required
@admin_required
def admin_vendor_reject(request, vendor_id):
    """Admin action to reject vendor application."""
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', 'Did not meet requirements.')
        vendor.status = 'REJECTED'
        vendor.rejection_reason = reason
        vendor.save()
        messages.warning(request, f"Vendor '{vendor.store_name}' has been rejected.")
    return redirect('dashboards:admin_vendors')
