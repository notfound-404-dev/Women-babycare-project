from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View
from django.http import JsonResponse

from .forms import (
    RegisterForm, DetailedProfileForm, QuickProfileForm, LoginForm, 
    AccountSettingsForm, CustomPasswordChangeForm, PersonalInfoForm, 
    AddressForm, ParentalInfoForm, PregnancyInfoForm, HealthInfoForm
)
from .models import UserProfile


class UserRegisterView(CreateView):
    """Registration view collecting full name, email, mobile, password."""
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        mobile = form.cleaned_data.get("mobile_number", "")
        if mobile:
            user.profile.mobile_number = mobile
            user.profile.save()
        messages.success(self.request, "Registration successful. Please login.")
        return redirect(self.success_url)


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


class ProfileView(LoginRequiredMixin, View):
    """Handle profile updates including account settings, password change, and profile info."""
    template_name = "accounts/profile.html"
    
    def get(self, request, *args, **kwargs):
        """Display all forms."""
        user = request.user
        profile = user.profile
        
        account_form = AccountSettingsForm(instance=user)
        password_form = CustomPasswordChangeForm(user)
        personal_form = PersonalInfoForm(instance=profile)
        address_form = AddressForm(instance=profile)
        parental_form = ParentalInfoForm(instance=profile)
        pregnancy_form = PregnancyInfoForm(instance=profile)
        health_form = HealthInfoForm(instance=profile)
        
        context = {
            "account_form": account_form,
            "password_form": password_form,
            "personal_form": personal_form,
            "address_form": address_form,
            "parental_form": parental_form,
            "pregnancy_form": pregnancy_form,
            "health_form": health_form,
            "form": personal_form,  # Keep 'form' for compatibility
            "title": "Complete Your Profile"
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle form submissions."""
        user = request.user
        profile = user.profile
        form_type = request.POST.get("form_type", "profile")
        
        # Get all forms for context (in case we need to re-render)
        account_form = AccountSettingsForm(instance=user)
        password_form = CustomPasswordChangeForm(user)
        personal_form = PersonalInfoForm(instance=profile)
        address_form = AddressForm(instance=profile)
        parental_form = ParentalInfoForm(instance=profile)
        pregnancy_form = PregnancyInfoForm(instance=profile)
        health_form = HealthInfoForm(instance=profile)
        
        # Handle Account Settings Form
        if form_type == "account":
            account_form = AccountSettingsForm(request.POST, instance=user)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "Email updated successfully.")
                return redirect("accounts:profile")
        
        # Handle Password Change Form
        elif form_type == "password":
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully.")
                return redirect("accounts:profile")
        
        # Handle Personal Info Form
        elif form_type == "personal":
            personal_form = PersonalInfoForm(request.POST, instance=profile)
            if personal_form.is_valid():
                personal_form.save()
                messages.success(request, "Personal information updated successfully.")
                return redirect("accounts:profile")
        
        # Handle Address Form
        elif form_type == "address":
            address_form = AddressForm(request.POST, instance=profile)
            if address_form.is_valid():
                address_form.save()
                messages.success(request, "Delivery address updated successfully.")
                return redirect("accounts:profile")
        
        # Handle Parental Info Form
        elif form_type == "parental":
            parental_form = ParentalInfoForm(request.POST, instance=profile)
            if parental_form.is_valid():
                parental_form.save()
                messages.success(request, "Parental information updated successfully.")
                return redirect("accounts:profile")
        
        # Handle Pregnancy Info Form
        elif form_type == "pregnancy":
            pregnancy_form = PregnancyInfoForm(request.POST, instance=profile)
            if pregnancy_form.is_valid():
                pregnancy_form.save()
                messages.success(request, "Pregnancy information updated successfully.")
                return redirect("accounts:profile")
        
        # Handle Health Info Form
        elif form_type == "health":
            health_form = HealthInfoForm(request.POST, instance=profile)
            if health_form.is_valid():
                health_form.save()
                messages.success(request, "Health information updated successfully.")
                return redirect("accounts:profile")
        
        context = {
            "account_form": account_form,
            "password_form": password_form,
            "personal_form": personal_form,
            "address_form": address_form,
            "parental_form": parental_form,
            "pregnancy_form": pregnancy_form,
            "health_form": health_form,
            "form": personal_form,
            "title": "Complete Your Profile"
        }
        return render(request, self.template_name, context)


class QuickAddressView(LoginRequiredMixin, UpdateView):
    """Quick address form for checkout."""
    model = UserProfile
    form_class = QuickProfileForm
    template_name = "accounts/quick_address.html"
    success_url = reverse_lazy("orders:checkout")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Address saved. Proceeding to checkout.")
        return super().form_valid(form)


class DeleteUserAccountView(LoginRequiredMixin, View):
    """Delete user account and associated profile."""
    
    def post(self, request, *args, **kwargs):
        user = request.user
        user_email = user.email
        
        # Delete user (profile will cascade delete)
        user.delete()
        
        messages.success(request, f"Account for {user_email} has been deleted successfully.")
        return redirect("accounts:register")
