from django.urls import path

from .views import AddToCartView, CartSummaryView, RemoveCartItemView, UpdateCartItemView, UpdateCartItemAjaxView

app_name = "cart"

urlpatterns = [
    path("", CartSummaryView.as_view(), name="summary"),
    path("add/<int:product_id>/", AddToCartView.as_view(), name="add"),
    path("update/<int:item_id>/", UpdateCartItemView.as_view(), name="update"),
    path("update-ajax/<int:item_id>/", UpdateCartItemAjaxView.as_view(), name="update_ajax"),
    path("remove/<int:item_id>/", RemoveCartItemView.as_view(), name="remove"),
]
