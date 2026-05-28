from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import UserProfile


class RegisterForm(UserCreationForm):
    """Registration form with full name, email, mobile."""
    email = forms.EmailField(required=True, label="Email Address")
    first_name = forms.CharField(max_length=50, required=True, label="Full Name")
    mobile_number = forms.CharField(max_length=20, required=False, label="Mobile Number")

    class Meta:
        model = User
        fields = ("first_name", "email", "mobile_number", "password1", "password2")

    def clean_email(self):
        """Validate email is unique and not already registered."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email or login.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class DetailedProfileForm(forms.ModelForm):
    """Complete profile form for address, personal & parental information."""
    class Meta:
        model = UserProfile
        fields = [
            "date_of_birth", "gender", "marital_status",
            "house_number", "street_name", "city", "state", "pincode", "country",
            "is_default_address",
            "is_parent", "baby_age_group", "baby_gender",
            "pregnancy_stage", "health_condition"
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "marital_status": forms.Select(attrs={"class": "form-select"}),
            "house_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "House/Flat Number"}),
            "street_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Street Name"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Pincode"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "is_default_address": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_parent": forms.Select(attrs={"class": "form-select"}),
            "baby_age_group": forms.Select(attrs={"class": "form-select"}),
            "baby_gender": forms.Select(attrs={"class": "form-select"}),
            "pregnancy_stage": forms.Select(attrs={"class": "form-select"}),
            "health_condition": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Any health conditions or allergies"}),
        }


class PersonalInfoForm(forms.ModelForm):
    """Form for personal information only."""
    class Meta:
        model = UserProfile
        fields = ["date_of_birth", "gender", "marital_status"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control profile-input"}),
            "gender": forms.Select(attrs={"class": "form-select profile-input"}),
            "marital_status": forms.Select(attrs={"class": "form-select profile-input"}),
        }


class AddressForm(forms.ModelForm):
    """Form for delivery address information only."""
    class Meta:
        model = UserProfile
        fields = ["house_number", "street_name", "city", "state", "pincode", "country", "is_default_address"]
        widgets = {
            "house_number": forms.TextInput(attrs={"class": "form-control profile-input", "placeholder": "House/Flat Number"}),
            "street_name": forms.TextInput(attrs={"class": "form-control profile-input", "placeholder": "Street Name"}),
            "city": forms.TextInput(attrs={"class": "form-control profile-input", "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": "form-control profile-input", "placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"class": "form-control profile-input", "placeholder": "Pincode"}),
            "country": forms.TextInput(attrs={"class": "form-control profile-input"}),
            "is_default_address": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ParentalInfoForm(forms.ModelForm):
    """Form for parental information only."""
    class Meta:
        model = UserProfile
        fields = ["is_parent", "baby_age_group", "baby_gender"]
        widgets = {
            "is_parent": forms.Select(attrs={"class": "form-select profile-input"}),
            "baby_age_group": forms.Select(attrs={"class": "form-select profile-input"}),
            "baby_gender": forms.Select(attrs={"class": "form-select profile-input"}),
        }


class PregnancyInfoForm(forms.ModelForm):
    """Form for pregnancy information only."""
    class Meta:
        model = UserProfile
        fields = ["pregnancy_stage"]
        widgets = {
            "pregnancy_stage": forms.Select(attrs={"class": "form-select profile-input"}),
        }


class HealthInfoForm(forms.ModelForm):
    """Form for health and allergies information only."""
    class Meta:
        model = UserProfile
        fields = ["health_condition"]
        widgets = {
            "health_condition": forms.Textarea(attrs={"class": "form-control profile-input", "rows": 3, "placeholder": "Any health conditions or allergies"}),
        }


class QuickProfileForm(forms.ModelForm):
    """Minimal form for address info during checkout."""
    class Meta:
        model = UserProfile
        fields = ["house_number", "street_name", "city", "state", "pincode", "country"]
        widgets = {
            "house_number": forms.TextInput(attrs={"class": "form-control"}),
            "street_name": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "pincode": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
        }


class LoginForm(AuthenticationForm):
    """Custom login form using email instead of username."""
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "autofocus": True,
            "placeholder": "Enter your registered email"
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "current-password",
            "placeholder": "Enter your password"
        })
    )


class AccountSettingsForm(forms.ModelForm):
    """Form for updating email address."""
    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control profile-input",
                "placeholder": "Enter your email address"
            })
        }

    def clean_email(self):
        """Validate email is unique (excluding current user)."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already registered. Please use a different email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Also update username to match email (to keep them in sync)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styled widgets."""
    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control profile-input",
            "placeholder": "Enter your current password",
            "autocomplete": "current-password"
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control profile-input",
            "placeholder": "Enter your new password",
            "autocomplete": "new-password"
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control profile-input",
            "placeholder": "Confirm your new password",
            "autocomplete": "new-password"
        })
    )
