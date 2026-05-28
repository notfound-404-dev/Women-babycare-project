from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from apps.orders.models import OrderItem
from apps.products.models import Product

from .models import SearchHistory


class RecommendationListView(LoginRequiredMixin, ListView):
    template_name = "personalization/recommendations.html"
    context_object_name = "products"

    def get_queryset(self):
        user = self.request.user

        purchased_ids = OrderItem.objects.filter(order__user=user).values_list("product_id", flat=True)
        search_terms = SearchHistory.objects.filter(user=user).values_list("query", flat=True)[:10]
        profile_age = user.profile.baby_age_group if hasattr(user, "profile") else ""

        query = Q(pk__in=purchased_ids)
        for term in search_terms:
            query |= Q(name__icontains=term) | Q(description__icontains=term)
        if profile_age:
            query |= Q(baby_age_group=profile_age)

        return Product.objects.filter(is_active=True).filter(query).distinct()[:20]
