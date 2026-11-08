
from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PROCESSING = "PROCESSING", "Processing"
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        PAID = "PAID", "Paid"

    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    vendor_name = models.CharField(max_length=255, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    tax_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )

    currency = models.CharField(max_length=10, default="INR")

    invoice_file = models.FileField(
        upload_to="invoices/", blank=True, null=True
    )

    extracted_text = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED
    )

    is_duplicate = models.BooleanField(default=False)
    validation_message = models.TextField(blank=True, null=True)
    validation_status = models.CharField(max_length=20, default="PENDING")

    # Approval information
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_invoices"
    )

    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number or f"Invoice {self.id}"


class InvoiceApproval(models.Model):

    class Action(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="approval_history"
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.action}"
