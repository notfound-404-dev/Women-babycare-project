import uuid
from datetime import timedelta

import razorpay
import logging
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from apps.accounts.models import UserProfile
from apps.cart.models import Cart
from apps.notifications_app.models import Notification

from .models import Order, OrderItem, Payment, OrderTracking

logger = logging.getLogger(__name__)


class CheckoutView(LoginRequiredMixin, View):
    """Simulated payment flow (testing mode only) with address validation."""

    success_url = reverse_lazy("orders:list")

    def get(self, request):
        """Display checkout page with order summary."""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("cart:summary")

        # Get or create user profile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # Check if address is complete
        if not (profile.house_number and profile.street_name and profile.city and profile.state and profile.pincode):
            messages.warning(request, "Please provide your delivery address to proceed.")
            return redirect("accounts:quick_address")
        
        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        
        context = {
            "cart": cart,
            "profile": profile,
            "total": total,
            "item_count": cart.items.count(),
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }
        return render(request, "orders/checkout.html", context)

    def post(self, request):
        """Initiate Razorpay payment."""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("cart:summary")

        # Get or create user profile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # Check if address is complete
        if not (profile.house_number and profile.street_name and profile.city and profile.state and profile.pincode):
            messages.warning(request, "Please provide your delivery address to proceed.")
            return redirect("accounts:quick_address")
        
        # Create order object first
        order = Order.objects.create(
            user=request.user,
            shipping_address=profile.get_full_address(),
            payment_status="pending",
            status="created",
        )

        # Add items to order
        total = 0
        for item in cart.items.select_related("product"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            total += item.product.price * item.quantity

        order.total_amount = total
        order.save()

        # Create Payment record first
        payment = Payment.objects.create(
            order=order,
            provider="Razorpay",
            transaction_id=f"PENDING-{uuid.uuid4().hex[:12].upper()}",
            status="pending",
        )

        try:
            # Initialize Razorpay client
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(total * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': 1,  # Auto capture payment
                'notes': {
                    'order_id': order.id,
                    'user_id': request.user.id,
                }
            })

            logger.info("Razorpay order created: %s for local order %s", razorpay_order.get('id'), order.order_id)

            # Update Payment with Razorpay order ID
            payment.transaction_id = razorpay_order['id']
            payment.save()

            context = {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                'amount': int(total * 100),
                'amount_in_rupees': total,
                'currency': 'INR',
                'user_name': request.user.get_full_name() or request.user.username,
                'user_email': request.user.email,
                'user_phone': profile.phone_number if hasattr(profile, 'phone_number') else '9999999999',
                'order_id': order.id,
            }

            return render(request, "orders/razorpay_payment.html", context)
        
        except Exception as e:
            # If Razorpay fails, use test payment mode
            logger.exception("Razorpay order creation failed for order %s", order.order_id)
            payment.provider = "TestPayment"
            payment.transaction_id = f"TEST-{uuid.uuid4().hex[:12].upper()}"
            payment.status = "failed"
            payment.save()
            order.payment_status = "failed"
            order.status = "created"
            order.save()

            # Use test payment template
            context = {
                'order_id': order.id,
                'amount': total,
                'currency': 'INR',
                'user_name': request.user.get_full_name() or request.user.username,
                'error_message': f"Razorpay connection failed. Using Test Payment Mode. Error: {str(e)[:100]}",
            }

            return render(request, "orders/test_payment.html", context)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            payment_status="success",
        ).prefetch_related("items")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            payment_status="success",
        ).prefetch_related("items__product")


class CancelOrderView(LoginRequiredMixin, View):
    """Handle order cancellation"""
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order can be cancelled
        if not order.can_cancel():
            messages.error(request, "This order cannot be cancelled. It may have already been shipped or more than 24 hours have passed.")
            return redirect("orders:detail", pk=order_id)
        
        # Cancel the order
        order.status = "cancelled"
        order.cancelled_at = timezone.now()
        order.save()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            title="Order cancelled",
            message=f"Your order {order.order_id} has been successfully cancelled.",
            notification_type="order_update",
        )
        
        messages.success(request, f"Order {order.order_id} has been cancelled successfully.")
        return redirect("orders:detail", pk=order_id)


class OrderTrackingView(LoginRequiredMixin, DetailView):
    """Display detailed tracking information for an order"""
    model = Order
    template_name = "orders/order_tracking.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("tracking_updates")


class TrackingUpdateView(LoginRequiredMixin, View):
    """Display all tracking updates for an order"""
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        tracking_updates = order.tracking_updates.all()
        
        context = {
            "order": order,
            "tracking_updates": tracking_updates,
        }
        return render(request, "orders/tracking_updates.html", context)


class RazorpayCallbackView(LoginRequiredMixin, View):
    """Handle Razorpay payment callback."""

    def post(self, request):
        """Verify Razorpay payment signature."""
        try:
            payment_data = request.POST
            
            # Verify Razorpay signature
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            # This verifies the signature (throws exception if invalid)
            client.utility.verify_payment_signature({
                'razorpay_order_id': payment_data.get('razorpay_order_id'),
                'razorpay_payment_id': payment_data.get('razorpay_payment_id'),
                'razorpay_signature': payment_data.get('razorpay_signature'),
            })

            # Payment is verified, update order
            order_id = request.POST.get('order_id')
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Update order and payment status
            order.payment_status = "success"
            order.status = "ordered"
            order.save()
            
            # Update payment record
            payment = order.payment
            payment.status = "success"
            payment.transaction_id = payment_data.get('razorpay_payment_id')
            payment.save()
            
            # Clear cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart.items.all().delete()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title="Payment successful",
                message=f"Your order {order.order_id} has been placed successfully.",
                notification_type="order_update",
            )
            
            messages.success(request, f"Payment successful! Order ID: {order.order_id}")
            return redirect("orders:detail", pk=order.id)
        except razorpay.BadRequestError as bre:
            logger.warning("Razorpay signature verification failed: %s", str(bre))
            # Try to mark payment failed
            order_id = request.POST.get('order_id')
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                order.payment_status = "failed"
                order.status = "created"
                order.save()
                payment = order.payment
                payment.status = "failed"
                payment.save()
            except Exception:
                logger.exception("Failed to update order/payment after BadRequestError")
            messages.error(request, "Payment verification failed. Invalid payment.")
            return redirect("orders:checkout")
        except Exception as e:
            logger.exception("Unexpected error in RazorpayCallbackView: %s", str(e))
            # Try to mark payment failed
            order_id = request.POST.get('order_id')
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                order.payment_status = "failed"
                order.status = "created"
                order.save()
                payment = order.payment
                payment.status = "failed"
                payment.save()
            except Exception:
                logger.exception("Failed to update order/payment after exception")
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect("orders:checkout")


class RazorpayFailureLogView(LoginRequiredMixin, View):
    """Receive client-side Razorpay failure payload for logging."""

    def post(self, request):
        try:
            data = request.POST.dict()
            logger.warning("Razorpay client payment.failed: %s", data)
            order_id = data.get("order_id")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, user=request.user)
                    order.payment_status = "failed"
                    order.status = "created"
                    order.save()
                    payment = order.payment
                    payment.status = "failed"
                    payment.save()
                except Exception:
                    logger.exception("Failed to update order/payment for order_id=%s", order_id)
            return JsonResponse({"ok": True})
        except Exception as e:
            logger.exception("Failed to record razorpay failure: %s", str(e))
            return JsonResponse({"ok": False, "error": str(e)}, status=500)


class TestPaymentConfirmView(LoginRequiredMixin, View):
    """Handle test payment confirmation."""

    def post(self, request):
        """Confirm test payment and create order."""
        try:
            order_id = request.POST.get('order_id')
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Update order status
            order.payment_status = "success"
            order.status = "ordered"
            order.save()
            
            # Update payment record
            payment = order.payment
            payment.status = "success"
            payment.save()
            
            # Clear cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart.items.all().delete()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title="Test payment successful",
                message=f"Your test order {order.order_id} has been placed successfully.",
                notification_type="order_update",
            )
            
            messages.success(request, f"Test payment successful! Order ID: {order.order_id}")
            return redirect("orders:detail", pk=order.id)
            
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect("orders:checkout")
        except Exception as e:
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect("orders:checkout")
