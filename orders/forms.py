from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-indigo-600 focus:ring-indigo-500'})
    )

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'shipping_address', 'city', 'postal_code', 'notes', 'payment_method']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'placeholder': 'Mobile Phone Number'}),
            'shipping_address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'rows': 3, 'placeholder': 'Street Address / Landmark'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'placeholder': 'City (e.g. Kathmandu, Pokhara)'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'placeholder': 'Postal Code (Optional)'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'rows': 2, 'placeholder': 'Special instructions for delivery (Optional)'}),
        }
