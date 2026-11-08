
from django.db import models


class Invoice(models.Model):

    STATUS_CHOICES = [
        ("UPLOADED", "Uploaded"),
        ("PROCESSING", "Processing"),
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("PAID", "Paid"),
        PAID = "PAID", "Paid"
    ]

    VALIDATION_CHOICES = [
        ("PENDING", "Pending"),
        ("VALID", "Valid"),
        ("INVALID", "Invalid"),
        ("REVIEW", "Needs Review"),
    ]

    # Invoice details
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    vendor_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    invoice_date = models.DateField(
        blank=True,
        null=True,
    )

    due_date = models.DateField(
        blank=True,
        null=True,
    )

    # Financial details
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    currency = models.CharField(
        max_length=10,
        default="INR",
    )

    # Uploaded invoice document
    invoice_file = models.FileField(
        upload_to="invoices/",
    )

    # OCR output
    extracted_text = models.TextField(
        blank=True,
        null=True,
    )

    # Processing and validation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="UPLOADED",
    )

    validation_status = models.CharField(
        max_length=20,
        choices=VALIDATION_CHOICES,
        default="PENDING",
    )

    validation_message = models.TextField(
        blank=True,
        null=True,
    )

    # Duplicate detection
    is_duplicate = models.BooleanField(
        default=False,
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.invoice_number or f"Invoice {self.id}"
