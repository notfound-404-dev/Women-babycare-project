from django.urls import path

from .views import ProfileView, QuickAddressView, UserLoginView, UserLogoutView, UserRegisterView, DeleteUserAccountView

app_name = "accounts"

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("quick-address/", QuickAddressView.as_view(), name="quick_address"),
    path("delete-account/", DeleteUserAccountView.as_view(), name="delete_account"),
]
