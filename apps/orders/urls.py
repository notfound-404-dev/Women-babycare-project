from django.urls import path

from .views import CheckoutView, OrderDetailView, OrderListView, CancelOrderView, OrderTrackingView, TrackingUpdateView, RazorpayCallbackView, TestPaymentConfirmView, RazorpayFailureLogView

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path("<int:order_id>/cancel/", CancelOrderView.as_view(), name="cancel"),
    path("<int:pk>/tracking/", OrderTrackingView.as_view(), name="tracking"),
    path("<int:order_id>/tracking-updates/", TrackingUpdateView.as_view(), name="tracking_updates"),
    path("razorpay/callback/", RazorpayCallbackView.as_view(), name="razorpay_callback"),
    path("razorpay/failure/", RazorpayFailureLogView.as_view(), name="razorpay_failure"),
    path("test-payment/confirm/", TestPaymentConfirmView.as_view(), name="test_payment_confirm"),
]
