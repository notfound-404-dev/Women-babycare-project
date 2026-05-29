from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.products.models import Product

from .models import Cart, CartItem


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartSummaryView(LoginRequiredMixin, TemplateView):
    template_name = "cart/cart_summary.html"

    def get(self, request, *args, **kwargs):
        pending = request.session.pop("pending_add_to_cart", None)
        if pending:
            product_id = pending.get("product_id")
            product = Product.objects.filter(pk=product_id, is_active=True).first()
            if not product:
                messages.error(request, "The requested product is no longer available.")
            else:
                try:
                    quantity = int(pending.get("quantity", 1))
                except (TypeError, ValueError):
                    quantity = 1

                if quantity <= 0:
                    quantity = 1

                if product.stock <= 0:
                    messages.error(request, f"{product.name} is out of stock.")
                else:
                    cart = get_or_create_cart(request.user)
                    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                    new_quantity = quantity if created else item.quantity + quantity

                    if new_quantity > product.stock:
                        messages.error(
                            request,
                            f"Only {product.stock} item(s) left in stock for {product.name}.",
                        )
                    else:
                        item.quantity = new_quantity
                        item.save()
                        messages.success(request, f"{product.name} added to cart.")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_or_create_cart(self.request.user)
        return context


class AddToCartView(LoginRequiredMixin, View):
    def handle_no_permission(self):
        product_id = self.kwargs.get("product_id")
        quantity = self.request.POST.get("quantity")
        if product_id:
            self.request.session["pending_add_to_cart"] = {
                "product_id": product_id,
                "quantity": quantity or "1",
            }
        return redirect_to_login(
            next=reverse("cart:summary"),
            login_url=self.get_login_url(),
            redirect_field_name=self.get_redirect_field_name(),
        )

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = int(request.POST.get("quantity", 1))

        if quantity <= 0:
            quantity = 1

        if product.stock <= 0:
            messages.error(request, f"{product.name} is out of stock.")
            return redirect(request.META.get("HTTP_REFERER", "products:list"))

        cart = get_or_create_cart(request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        new_quantity = quantity if created else item.quantity + quantity

        if new_quantity > product.stock:
            messages.error(request, f"Only {product.stock} item(s) left in stock for {product.name}.")
            return redirect(request.META.get("HTTP_REFERER", "cart:summary"))

        item.quantity = new_quantity
        item.save()
        messages.success(request, f"{product.name} added to cart.")
        return redirect("cart:summary")


class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
        messages.success(request, "Cart updated.")
        return redirect("cart:summary")


class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        item.delete()
        messages.success(request, "Item removed from cart.")
        return redirect("cart:summary")


class UpdateCartItemAjaxView(LoginRequiredMixin, View):
    """AJAX endpoint for updating cart items without page reload"""
    def post(self, request, item_id):
        try:
            item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
            quantity = int(request.POST.get("quantity", 1))
            
            if quantity <= 0:
                item.delete()
                return JsonResponse({
                    "success": True,
                    "removed": True,
                    "cart_total": item.cart.get_total(),
                })
            else:
                item.quantity = quantity
                item.save()
                return JsonResponse({
                    "success": True,
                    "removed": False,
                    "item_subtotal": item.subtotal,
                    "cart_total": item.cart.get_total(),
                })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
