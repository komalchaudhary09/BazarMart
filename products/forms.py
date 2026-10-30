from django import forms
from .models import Product, Category, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'discount_price', 'stock', 'image', 'is_active', 'featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none'}),
            'image': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        if discount_price and price and discount_price >= price:
            self.add_error('discount_price', "Discount price must be less than the regular price.")
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
        }
