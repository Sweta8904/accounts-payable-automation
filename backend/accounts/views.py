from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import UserProfile
from .serializers import (
    CurrentUserSerializer,
    UserCreateSerializer,
)
from .permissions import IsAdmin


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.select_related("user").all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        return UserCreateSerializer

    def get_queryset(self):
        return UserProfile.objects.select_related("user").all()

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response

        profiles = self.get_queryset()

        data = [
            {
                "id": profile.user.id,
                "username": profile.user.username,
                "email": profile.user.email,
                "first_name": profile.user.first_name,
                "last_name": profile.user.last_name,
                "role": profile.role,
                "department": profile.department,
                "is_active": (
                    profile.is_active and profile.user.is_active
                ),
            }
            for profile in profiles
        ]

        return Response(data)