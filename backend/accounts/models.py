from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        FINANCE_MANAGER = "FINANCE_MANAGER", "Finance Manager"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        APPROVER = "APPROVER", "Approver"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.ACCOUNTANT
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"