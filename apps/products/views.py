from django.db.models import Q
from django.views.generic import DetailView, ListView

from apps.personalization.models import SearchHistory

from .models import Category, Product


class ProductListView(ListView):
    template_name = "products/product_list.html"
    model = Product
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        min_price = self.request.GET.get("min_price", "").strip()
        max_price = self.request.GET.get("max_price", "").strip()
        age_group = self.request.GET.get("age_group", "").strip()

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))
            if self.request.user.is_authenticated:
                SearchHistory.objects.create(user=self.request.user, query=q)
        if category:
            queryset = queryset.filter(category__slug=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if age_group:
            # Show products that match the selected age group OR products marked as "all ages"
            queryset = queryset.filter(Q(baby_age_group=age_group) | Q(baby_age_group="all"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["age_groups"] = Product.AGE_GROUP_CHOICES
        return context


class ProductDetailView(DetailView):
    template_name = "products/product_detail.html"
    model = Product
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        context["related_products"] = (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .order_by("-created_at")[:4]
        )
        context["product_highlights"] = [
            {"label": "Category", "value": product.category.name},
            {"label": "Age Group", "value": product.get_baby_age_group_display()},
            {"label": "Stock", "value": f"{product.stock} available" if product.stock > 0 else "Out of stock"},
            {"label": "Status", "value": "Ready to ship" if product.stock > 0 else "Currently unavailable"},
        ]
        context["what_in_the_box"] = [
            product.name,
            f"1 x {product.category.name}",
            "Packed securely for safe delivery",
        ]
        context["size_and_fit"] = [
            f"Suitable for: {product.get_baby_age_group_display()}",
            f"Weight / size guidance depends on the product variant and manufacturer specs for {product.category.name}.",
            "Please review the description and verify product suitability before purchase.",
        ]
        context["warranty_text"] = (
            f"Warranty coverage for {product.name} follows the brand or manufacturer policy. "
            "Please keep your invoice and packaging for any support claims."
        )
        return context
