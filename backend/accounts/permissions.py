from rest_framework.permissions import BasePermission

from .models import UserProfile


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser:
        return UserProfile.Role.ADMIN

    try:
        profile = user.profile

        if not profile.is_active:
            return None

        return profile.role

    except UserProfile.DoesNotExist:
        return None


class IsAdmin(BasePermission):
    message = "Only Admin users can perform this action."

    def has_permission(self, request, view):
        return get_user_role(request.user) == UserProfile.Role.ADMIN


class IsFinanceManager(BasePermission):
    message = "Finance Manager access required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in [
            UserProfile.Role.ADMIN,
            UserProfile.Role.FINANCE_MANAGER,
        ]


class IsAccountant(BasePermission):
    message = "Accountant access required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in [
            UserProfile.Role.ADMIN,
            UserProfile.Role.ACCOUNTANT,
        ]


class IsApprover(BasePermission):
    message = "Approver access required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in [
            UserProfile.Role.ADMIN,
            UserProfile.Role.APPROVER,
        ]


class IsFinanceTeam(BasePermission):
    message = "Finance team access required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in [
            UserProfile.Role.ADMIN,
            UserProfile.Role.FINANCE_MANAGER,
            UserProfile.Role.ACCOUNTANT,
        ]