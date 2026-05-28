from django.contrib import admin

from .models import Order, OrderItem, Payment, OrderTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    fields = ("status", "location", "description", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "status", "payment_status", "total_amount", "created_at")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_id", "user__username")
    inlines = [OrderItemInline, OrderTrackingInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'shipping_address', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Order Status', {
            'fields': ('status', 'payment_status', 'cancelled_at')
        }),
    )
    readonly_fields = ('order_id', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update order tracking when status changes
        if change and 'status' in form.changed_data:
            OrderTracking.objects.create(
                order=obj,
                status=obj.status,
                description=f"Order status updated to {obj.get_status_display()} by admin"
            )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order", "provider", "status", "created_at")


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "location", "updated_at")
    list_filter = ("status", "updated_at")
    search_fields = ("order__order_id", "location")
