from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsFinanceTeam
from .models import Vendor
from .serializers import VendorSerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated, IsFinanceTeam]

    def get_queryset(self):
        queryset = Vendor.objects.all()

        search = self.request.query_params.get("search")
        status = self.request.query_params.get("status")

        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(vendor_code__icontains=search) |
                Q(email__icontains=search)
            )

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset