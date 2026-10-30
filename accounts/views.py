from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .forms import CustomerRegistrationForm, VendorRegistrationForm, UserProfileForm
from vendors.models import Vendor


def register_customer(request):
    if request.user.is_authenticated:
        return redirect('dashboards:dashboard_redirect')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'CUSTOMER'
            user.save()
            messages.success(request, f"Welcome {user.username}! Your customer account has been created.")
            login(request, user)
            return redirect('dashboards:customer_dashboard')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register_customer.html', {'form': form})


def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('dashboards:dashboard_redirect')

    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.role = 'VENDOR'
                user.save()

                Vendor.objects.create(
                    user=user,
                    store_name=form.cleaned_data['store_name'],
                    description=form.cleaned_data.get('store_description', ''),
                    address=form.cleaned_data.get('store_address', ''),
                    phone=form.cleaned_data.get('phone', ''),
                    logo=form.cleaned_data.get('logo'),
                    status='PENDING'
                )

            messages.success(
                request,
                "Vendor registration successful! Your account is pending administrator approval. "
                "You can log in to view your application status."
            )
            login(request, user)
            return redirect('dashboards:vendor_dashboard')
    else:
        form = VendorRegistrationForm()

    return render(request, 'accounts/register_vendor.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboards:dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboards:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('products:product_list')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated successfully!")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
