from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render

from apps.orders.models import Order
from apps.products.models import Product


@staff_member_required
def admin_dashboard(request):
    context = {
        "users_count": User.objects.count(),
        "products_count": Product.objects.count(),
        "orders_count": Order.objects.count(),
        "sales_total": Order.objects.filter(payment_status="success").aggregate(total=Sum("total_amount"))["total"] or 0,
        "recent_orders": Order.objects.select_related("user")[:10],
    }
    return render(request, "dashboard/admin_dashboard.html", context)
