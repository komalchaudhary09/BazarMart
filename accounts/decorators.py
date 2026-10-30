from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles=None):
    """
    Decorator to restrict view access to specific user roles.
    allowed_roles: list or tuple of roles e.g. ['ADMIN', 'VENDOR']
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')

            if request.user.is_superuser or request.user.role in allowed_roles:
                # If role is VENDOR, verify vendor approval status
                if request.user.role == 'VENDOR' and 'VENDOR' in allowed_roles and not request.user.is_superuser:
                    vendor_profile = getattr(request.user, 'vendor_profile', None)
                    if not vendor_profile or vendor_profile.status != 'APPROVED':
                        messages.warning(
                            request,
                            "Your vendor account is pending approval by the admin. You will gain access once approved."
                        )
                        return redirect('dashboards:vendor_dashboard')

                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access that resource.")
            return redirect('dashboards:dashboard_redirect')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator requiring ADMIN role or superuser."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with admin privileges.")
            return redirect('accounts:login')
        if not (request.user.role == 'ADMIN' or request.user.is_superuser):
            messages.error(request, "Admin access required.")
            return redirect('dashboards:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def vendor_required(view_func):
    """Decorator requiring approved VENDOR role."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to your vendor account.")
            return redirect('accounts:login')
        if not (request.user.role == 'VENDOR' or request.user.is_superuser):
            messages.error(request, "Vendor access required.")
            return redirect('dashboards:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def customer_required(view_func):
    """Decorator requiring CUSTOMER role or superuser."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to continue.")
            return redirect('accounts:login')
        if not (request.user.role == 'CUSTOMER' or request.user.is_superuser):
            messages.error(request, "Customer access required.")
            return redirect('dashboards:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
