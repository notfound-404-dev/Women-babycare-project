from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    MARITAL_STATUS_CHOICES = [("single", "Single"), ("married", "Married"), ("divorced", "Divorced"), ("widowed", "Widowed")]
    PARENT_CHOICES = [("yes", "Yes"), ("no", "No"), ("planning", "Planning")]
    PREGNANCY_STAGE_CHOICES = [
        ("planning", "Planning Pregnancy"),
        ("1st", "1st Trimester"),
        ("2nd", "2nd Trimester"),
        ("3rd", "3rd Trimester"),
        ("postpartum", "Postpartum"),
    ]
    BABY_AGE_GROUP_CHOICES = [
        ("newborn", "Newborn (0–3 months)"),
        ("infant", "Infant (3–12 months)"),
        ("toddler", "Toddler (1–3 years)"),
        ("preschool", "Preschool (3+ years)"),
    ]
    BABY_GENDER_CHOICES = [("M", "Boy"), ("F", "Girl"), ("unknown", "Not Known")]

    # User relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Registration info
    mobile_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)

    # Address fields
    house_number = models.CharField(max_length=50, blank=True)
    street_name = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, blank=True, default="India")
    is_default_address = models.BooleanField(default=False)

    # Parental information
    is_parent = models.CharField(max_length=20, choices=PARENT_CHOICES, blank=True)
    baby_age_group = models.CharField(max_length=20, choices=BABY_AGE_GROUP_CHOICES, blank=True)
    baby_gender = models.CharField(max_length=10, choices=BABY_GENDER_CHOICES, blank=True)

    # Pregnancy information
    pregnancy_stage = models.CharField(max_length=20, choices=PREGNANCY_STAGE_CHOICES, blank=True)

    # Health & preferences
    health_condition = models.CharField(max_length=120, blank=True)
    profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile({self.user.username})"

    def get_full_address(self) -> str:
        parts = [self.house_number, self.street_name, self.city, self.state, self.pincode, self.country]
        return ", ".join([p for p in parts if p])
