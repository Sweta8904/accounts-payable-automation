
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from django.shortcuts import get_object_or_404

from invoices.models import Invoice
from .models import InvoiceMatch
from accounts.permissions import IsFinanceTeam
from .models import PurchaseOrder, GoodsReceiptNote
from .serializers import (
    PurchaseOrderSerializer,
    GoodsReceiptNoteSerializer,
)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, IsFinanceTeam]

    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related("vendor").prefetch_related("items")

        status = self.request.query_params.get("status")
        search = self.request.query_params.get("search")

        if status:
            queryset = queryset.filter(status=status.upper())

        if search:
            queryset = queryset.filter(
                po_number__icontains=search
            ) | queryset.filter(vendor__name__icontains=search)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GoodsReceiptNoteViewSet(viewsets.ModelViewSet):
    serializer_class = GoodsReceiptNoteSerializer
    permission_classes = [IsAuthenticated, IsFinanceTeam]

    def get_queryset(self):
        queryset = GoodsReceiptNote.objects.select_related(
            "purchase_order", "purchase_order__vendor"
        ).prefetch_related("items")

        po_id = self.request.query_params.get("purchase_order")
        if po_id:
            queryset = queryset.filter(purchase_order_id=po_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)

class InvoiceMatchingView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceTeam]

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, pk=invoice_id)

        po_id = request.data.get("purchase_order")
        if not po_id:
            return Response(
                {"error": "Purchase order ID is required."},
                status=http_status.HTTP_400_BAD_REQUEST
            )

        purchase_order = get_object_or_404(
            PurchaseOrder.objects.select_related("vendor").prefetch_related(
                "items", "goods_receipts__items"
            ),
            pk=po_id
        )

        differences = []

        # 1. Vendor matching
        invoice_vendor = (invoice.vendor_name or "").strip().casefold()
        po_vendor = purchase_order.vendor.name.strip().casefold()

        if not invoice_vendor or invoice_vendor != po_vendor:
            differences.append({
                "check": "VENDOR",
                "message": "Invoice vendor does not match PO vendor."
            })

        # 2. Calculate PO total including item-level tax
        po_amount = Decimal("0.00")

        for item in purchase_order.items.all():
            line_amount = item.quantity * item.unit_price
            tax = line_amount * item.tax_rate / Decimal("100")
            po_amount += line_amount + tax

        # 3. Calculate value of accepted goods
        received_amount = Decimal("0.00")

        for item in purchase_order.items.all():
            accepted_quantity = sum(
                (
                    receipt.accepted_quantity
                    for receipt in item.receipts.filter(
                        grn__status__in=["RECEIVED", "PARTIAL"]
                    )
                ),
                start=Decimal("0.00")
            )

            if accepted_quantity > item.quantity:
                differences.append({
                    "check": "QUANTITY",
                    "message": f"Accepted quantity exceeds PO quantity for {item.description}."
                })

            accepted_value = accepted_quantity * item.unit_price
            accepted_tax = (
                accepted_value * item.tax_rate / Decimal("100")
            )
            received_amount += accepted_value + accepted_tax

        # 4. Compare invoice total with accepted goods value
        invoice_amount = invoice.total_amount or Decimal("0.00")

        if invoice_amount <= 0:
            differences.append({
                "check": "INVOICE_AMOUNT",
                "message": "Invoice amount must be greater than zero."
            })

        tolerance = Decimal("1.00")

        if abs(invoice_amount - received_amount) > tolerance:
            differences.append({
                "check": "RECEIVED_AMOUNT",
                "message": (
                    f"Invoice amount {invoice_amount} does not match "
                    f"accepted goods value {received_amount}."
                )
            })

        # 5. Check PO status
        if purchase_order.status in ["DRAFT", "CANCELLED", "CLOSED"]:
            differences.append({
                "check": "PO_STATUS",
                "message": f"Purchase order status is {purchase_order.status}."
            })

        # 6. Check invoice validation
        if invoice.validation_status != "VALID":
            differences.append({
                "check": "INVOICE_VALIDATION",
                "message": "Invoice has not passed basic validation."
            })

        match_status = (
            InvoiceMatch.MatchStatus.MATCHED
            if not differences
            else InvoiceMatch.MatchStatus.MISMATCH
        )

        match_record = InvoiceMatch.objects.create(
            invoice=invoice,
            purchase_order=purchase_order,
            status=match_status,
            invoice_amount=invoice_amount,
            po_amount=po_amount,
            received_amount=received_amount,
            differences=differences,
            matched_by=request.user
        )

        return Response({
            "message": (
                "Three-way matching successful."
                if match_status == "MATCHED"
                else "Three-way matching found discrepancies."
            ),
            "match_id": match_record.id,
            "status": match_status,
            "invoice": {
                "id": invoice.id,
                "number": invoice.invoice_number,
                "amount": str(invoice_amount),
                "vendor": invoice.vendor_name
            },
            "purchase_order": {
                "id": purchase_order.id,
                "number": purchase_order.po_number,
                "amount": str(po_amount),
                "vendor": purchase_order.vendor.name
            },
            "accepted_goods_value": str(received_amount),
            "differences": differences
        })
