
from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = [
            "id",
            "uploaded_by",
            "extracted_text",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_invoice_file(self, file):
        allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png"]

        filename = file.name.lower()

        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "Only PDF, JPG, JPEG and PNG files are allowed."
            )

        max_size = 10 * 1024 * 1024

        if file.size > max_size:
            raise serializers.ValidationError(
                "File size must not exceed 10 MB."
            )

        return file
read_only_fields = [
    "id",
    "uploaded_by",
    "extracted_text",
    "status",
    "is_duplicate",
    "validation_message",
    "validation_status",
    "created_at",
    "updated_at",
]