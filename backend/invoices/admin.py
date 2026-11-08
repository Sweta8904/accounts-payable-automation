
from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "invoice_number",
        "vendor_name",
        "invoice_date",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "invoice_date", "created_at")

    search_fields = (
        "invoice_number",
        "vendor_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
