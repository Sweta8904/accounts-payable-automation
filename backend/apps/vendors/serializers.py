from rest_framework import serializers
from .models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_vendor_code(self, value):
        value = value.strip().upper()

        queryset = Vendor.objects.filter(vendor_code__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This vendor code already exists."
            )

        return value