from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsFinanceTeam
from invoices.models import Invoice
from apps.payments.models import Payment
from apps.vendors.models import Vendor
from apps.purchase_orders.models import PurchaseOrder


class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceTeam]

    def get(self, request):
        today = timezone.localdate()

        invoice_totals = Invoice.objects.aggregate(
            total_amount=Sum("total_amount"),
            tax_amount=Sum("tax_amount"),
            total_count=Count("id"),
        )

        invoice_statuses = list(
            Invoice.objects.values("status")
            .annotate(count=Count("id"), amount=Sum("total_amount"))
            .order_by("status")
        )

        payment_totals = Payment.objects.filter(
            status="COMPLETED"
        ).aggregate(
            paid_amount=Sum("amount"),
            payment_count=Count("id"),
        )

        overdue = Invoice.objects.filter(
            due_date__lt=today
        ).exclude(status__in=["PAID", "REJECTED"])

        purchase_order_statuses = list(
            PurchaseOrder.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        return Response({
            "generated_at": timezone.now(),
            "invoices": {
                "total_count": invoice_totals["total_count"] or 0,
                "total_amount": invoice_totals["total_amount"] or Decimal("0.00"),
                "tax_amount": invoice_totals["tax_amount"] or Decimal("0.00"),
                "by_status": invoice_statuses,
            },
            "payments": {
                "completed_count": payment_totals["payment_count"] or 0,
                "completed_amount": payment_totals["paid_amount"] or Decimal("0.00"),
            },
            "vendors": {
                "total": Vendor.objects.count(),
                "active": Vendor.objects.filter(is_active=True).count(),
            },
            "purchase_orders": {
                "total": PurchaseOrder.objects.count(),
                "by_status": purchase_order_statuses,
            },
            "overdue_invoices": {
                "count": overdue.count(),
                "amount": overdue.aggregate(
                    total=Sum("total_amount")
                )["total"] or Decimal("0.00"),
            },
        })