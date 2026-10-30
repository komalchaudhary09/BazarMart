from .models import Category


def categories_processor(request):
    """Context processor returning active categories for global navigation."""
    categories = Category.objects.filter(is_active=True).order_by('name')
    return {
        'nav_categories': categories
    }
