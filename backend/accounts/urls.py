from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CurrentUserView,
    UserListCreateView,
)

urlpatterns = [
    # JWT authentication
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    # Current logged-in user
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current_user"
    ),

    # Admin-only user management
    path(
        "users/",
        UserListCreateView.as_view(),
        name="user_list_create"
    ),
]