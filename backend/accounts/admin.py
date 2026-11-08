from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "department",
        "is_active",
        "created_at",
    )

    list_filter = ("role", "is_active", "department")

    search_fields = (
        "user__username",
        "user__email",
        "department",
    )

    list_editable = ("role", "is_active")