from django.db import models
from django.contrib.auth.models import User
from apps.vendors.models import Vendor
from invoices.models import Invoice
from django.contrib.auth.models import User

class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        APPROVED = "APPROVED", "Approved"
        PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED", "Partially Received"
        RECEIVED = "RECEIVED", "Received"
        CLOSED = "CLOSED", "Closed"
        CANCELLED = "CANCELLED", "Cancelled"

    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, related_name="purchase_orders"
    )
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.DRAFT
    )
    currency = models.CharField(max_length=10, default="INR")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.po_number

    @property
    def total_amount(self):
        return sum(
            (item.quantity * item.unit_price for item in self.items.all()),
            start=0
        )


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    def __str__(self):
        return self.description


class GoodsReceiptNote(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        PARTIAL = "PARTIAL", "Partially Received"
        REJECTED = "REJECTED", "Rejected"

    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.PROTECT, related_name="goods_receipts"
    )
    received_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.RECEIVED
    )
    received_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.grn_number


class GoodsReceiptItem(models.Model):
    grn = models.ForeignKey(
        GoodsReceiptNote, on_delete=models.CASCADE, related_name="items"
    )
    purchase_order_item = models.ForeignKey(
        PurchaseOrderItem, on_delete=models.PROTECT, related_name="receipts"
    )
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    accepted_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.grn.grn_number} - {self.purchase_order_item.description}"

class InvoiceMatch(models.Model):
    class MatchStatus(models.TextChoices):
        MATCHED = "MATCHED", "Matched"
        MISMATCH = "MISMATCH", "Mismatch"
        REVIEW = "REVIEW", "Needs Review"

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="purchase_matches"
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.PROTECT, related_name="invoice_matches"
    )
    status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.REVIEW
    )
    invoice_amount = models.DecimalField(max_digits=15, decimal_places=2)
    po_amount = models.DecimalField(max_digits=15, decimal_places=2)
    received_amount = models.DecimalField(max_digits=15, decimal_places=2)
    differences = models.JSONField(default=list, blank=True)
    matched_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    matched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-matched_at"]

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.status}"