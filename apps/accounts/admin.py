from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile_number", "baby_age_group", "health_condition")
    search_fields = ("user__username", "user__email", "health_condition")
