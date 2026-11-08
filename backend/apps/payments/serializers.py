from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers

from .models import Payment
from invoices.models import Invoice


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True
    )
    vendor_name = serializers.CharField(
        source="invoice.vendor_name",
        read_only=True
    )

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "id",
            "recorded_by",
            "created_at",
        ]

    def validate(self, attrs):
        invoice = attrs.get(
            "invoice",
            self.instance.invoice if self.instance else None
        )

        amount = attrs.get(
            "amount",
            self.instance.amount if self.instance else None
        )

        status = attrs.get(
            "status",
            self.instance.status if self.instance else Payment.Status.PENDING
        )

        if invoice.status != Invoice.Status.APPROVED and invoice.status != Invoice.Status.PAID:
            raise serializers.ValidationError(
                "Only approved invoices can be paid."
            )

        if not invoice.purchase_matches.filter(status="MATCHED").exists():
            raise serializers.ValidationError(
                "A successful three-way match is required before payment."
            )

        if amount is None or amount <= 0:
            raise serializers.ValidationError(
                {"amount": "Payment amount must be greater than zero."}
            )

        completed_payments = Payment.objects.filter(
            invoice=invoice,
            status=Payment.Status.COMPLETED
        )

        if self.instance:
            completed_payments = completed_payments.exclude(
                pk=self.instance.pk
            )

        already_paid = completed_payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        if status == Payment.Status.COMPLETED:
            if already_paid + amount > invoice.total_amount:
                raise serializers.ValidationError(
                    "Completed payments cannot exceed the invoice total."
                )

        return attrs