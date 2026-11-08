
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from invoices.models import Invoice
from accounts.permissions import IsFinanceTeam
from apps.audit_logs.utils import log_action

from .models import Payment
from .serializers import PaymentSerializer


class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsFinanceTeam
    ]

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "invoice",
            "recorded_by"
        ).order_by("-created_at")

        invoice_id = self.request.query_params.get("invoice")
        status = self.request.query_params.get("status")

        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)

        if status:
            queryset = queryset.filter(status=status.upper())

        return queryset

    def perform_create(self, serializer):
        payment = serializer.save(recorded_by=self.request.user)

        log_action(
            user=self.request.user,
            action="PAYMENT_CREATED",
            entity_type="Payment",
            entity_id=payment.id,
            description=f"Payment {payment.payment_reference} created for invoice {payment.invoice_id}.",
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsFinanceTeam
    ]

    queryset = Payment.objects.select_related(
        "invoice",
        "recorded_by"
    )

    http_method_names = ["get", "patch", "head", "options"]

    @transaction.atomic
    def perform_update(self, serializer):
        payment = serializer.save()

        if payment.status == Payment.Status.COMPLETED:
            invoice = Invoice.objects.select_for_update().get(
                pk=payment.invoice_id
            )

            completed_total = Payment.objects.filter(
                invoice=invoice,
                status=Payment.Status.COMPLETED
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            if completed_total > invoice.total_amount:
                raise ValidationError(
                    "Completed payments cannot exceed the invoice total."
                )

            if completed_total >= invoice.total_amount:
                invoice.status = Invoice.Status.PAID
                invoice.save(
                    update_fields=["status", "updated_at"]
                )

        log_action(
            user=self.request.user,
            action="PAYMENT_UPDATED",
            entity_type="Payment",
            entity_id=payment.id,
            description=f"Payment {payment.payment_reference} updated to {payment.status}.",
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )
