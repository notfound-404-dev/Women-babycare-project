import uuid

from django.contrib.auth.models import User
from django.db import models

from apps.products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("ordered", "Ordered"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    shipping_address = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.order_id
    
    def can_cancel(self):
        """Check if order can be cancelled (within 24 hours and not already shipped/cancelled)"""
        from datetime import timedelta
        from django.utils import timezone
        
        if self.status in ['shipped', 'out_for_delivery', 'delivered', 'cancelled']:
            return False
        
        time_since_order = timezone.now() - self.created_at
        return time_since_order < timedelta(hours=24)
    
    def hours_until_cancel_deadline(self):
        """Get remaining hours before cancellation window closes"""
        from datetime import timedelta
        from django.utils import timezone
        
        if not self.can_cancel():
            return 0
        
        time_since_order = timezone.now() - self.created_at
        remaining = timedelta(hours=24) - time_since_order
        return max(0, int(remaining.total_seconds() / 3600))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=50, default="TestGateway")
    transaction_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=Order.PAYMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.transaction_id


class OrderTracking(models.Model):
    """Track order journey with timestamps and status updates"""
    TRACKING_STATUS = [
        ("ordered", "Order Placed"),
        ("processing", "Processing"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("in_transit", "In Transit"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tracking_updates")
    status = models.CharField(max_length=20, choices=TRACKING_STATUS)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-updated_at"]
    
    def __str__(self) -> str:
        return f"{self.order.order_id} - {self.get_status_display()}"
