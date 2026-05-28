from django.views.generic import TemplateView

from apps.products.models import Category, Product


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured products (first 8)
        featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        categories = Category.objects.all()
        
        context['featured_products'] = featured_products
        context['categories'] = categories
        
        return context
