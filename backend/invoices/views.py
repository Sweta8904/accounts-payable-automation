
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Invoice
from .serializers import InvoiceSerializer
from accounts.permissions import IsFinanceTeam
from .services.extraction_service import extract_invoice_fields
from .services.validation_service import validate_invoice

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Invoice, InvoiceApproval

from django.db.models import Count, Sum, Q

class InvoiceListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceTeam]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        invoices = Invoice.objects.all().order_by("-created_at")
        serializer = InvoiceSerializer(invoices, many=True)

        return Response({
            "status": "success",
            "count": invoices.count(),
            "invoices": serializer.data
        })

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        invoice = serializer.save(
            uploaded_by=request.user,
            status=Invoice.Status.PROCESSING
        )

        try:
            from .services.ocr_service import extract_invoice_text

            extracted_text = extract_invoice_text(invoice.invoice_file.path)
            invoice.extracted_text = extracted_text

            # Extract structured fields from OCR text.
            extracted = extract_invoice_fields(extracted_text)

            # Only fill fields that the uploader did not provide.
            for field in [
                "invoice_number",
                "vendor_name",
                "invoice_date",
                "due_date",
                "total_amount",
                "tax_amount",
            ]:
                extracted_value = extracted.get(field)
                if extracted_value is not None and not getattr(invoice, field):
                    setattr(invoice, field, extracted_value)

            invoice.status = Invoice.Status.PENDING
            invoice.save()

            # Run mandatory-field and duplicate checks.
            validation = validate_invoice(invoice)

            return Response({
                "status": "success",
                "message": "Invoice uploaded, OCR completed and validation performed.",
                "extracted_fields": extracted,
                "validation": validation,
                "invoice": InvoiceSerializer(invoice).data
            }, status=status.HTTP_201_CREATED)

        except Exception as error:
            invoice.validation_status = "OCR_FAILED"
            invoice.validation_message = str(error)
            invoice.save()

            return Response({
                "status": "partial_success",
                "message": "Invoice uploaded, but processing failed.",
                "processing_error": str(error),
                "invoice": InvoiceSerializer(invoice).data
            }, status=status.HTTP_201_CREATED)


class InvoiceApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def is_approver(self, user):
        if user.is_superuser:
            return True

        profile = getattr(user, "userprofile", None)
        return bool(
            profile and profile.role in ["ADMIN", "APPROVER"]
        )

    def post(self, request, pk):
        if not self.is_approver(request.user):
            return Response(
                {"message": "Only Admin or Approver can process invoices."},
                status=status.HTTP_403_FORBIDDEN
            )

        action = str(request.data.get("action", "")).upper()
        comments = str(request.data.get("comments", "")).strip()

        if action not in ["APPROVED", "REJECTED"]:
            return Response(
                {"message": "Action must be APPROVED or REJECTED."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == "REJECTED" and not comments:
            return Response(
                {"message": "Rejection reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            invoice = get_object_or_404(
                Invoice.objects.select_for_update(), pk=pk
            )

            if invoice.status != Invoice.Status.PENDING:
                return Response(
                    {"message": "Only pending invoices can be processed."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if action == "APPROVED":
                if invoice.validation_status != "VALID":
                    return Response({
                        "message": "Invoice validation must pass before approval.",
                        "validation_status": invoice.validation_status,
                        "validation_message": invoice.validation_message
                    }, status=status.HTTP_400_BAD_REQUEST)

                invoice.status = Invoice.Status.APPROVED
                invoice.approved_by = request.user
                invoice.approved_at = timezone.now()

            else:
                invoice.status = Invoice.Status.REJECTED
                invoice.rejection_reason = comments

            invoice.save()

            InvoiceApproval.objects.create(
                invoice=invoice,
                action=action,
                performed_by=request.user,
                comments=comments
            )

        return Response({
            "message": f"Invoice {action.lower()} successfully.",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "action_by": request.user.username
        })

    def get(self, request, pk):
        if not self.is_approver(request.user):
            return Response(
                {"message": "Only Admin or Approver can view history."},
                status=status.HTTP_403_FORBIDDEN
            )

        invoice = get_object_or_404(Invoice, pk=pk)

        history = invoice.approval_history.select_related("performed_by")

        return Response({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "history": [
                {
                    "action": item.action,
                    "performed_by": (
                        item.performed_by.username
                        if item.performed_by else None
                    ),
                    "comments": item.comments,
                    "created_at": item.created_at
                }
                for item in history
            ]
        })


class InvoiceDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceTeam]

    def get(self, request):
        invoices = Invoice.objects.all()

        # Count invoices by status
        total_invoices = invoices.count()
        uploaded = invoices.filter(status="UPLOADED").count()
        processing = invoices.filter(status="PROCESSING").count()
        pending = invoices.filter(status="PENDING").count()
        approved = invoices.filter(status="APPROVED").count()
        rejected = invoices.filter(status="REJECTED").count()

        # Count validation failures
        validation_failed = invoices.filter(
            validation_status="FAILED"
        ).count()

        # Calculate invoice amounts separately
        total_amount = invoices.aggregate(
            amount=Sum("total_amount")
        )["amount"] or 0

        pending_amount = invoices.filter(
            status="PENDING"
        ).aggregate(amount=Sum("total_amount"))["amount"] or 0

        approved_amount = invoices.filter(
            status="APPROVED"
        ).aggregate(amount=Sum("total_amount"))["amount"] or 0

        return Response({
            "status": "success",
            "dashboard": {
                "total_invoices": total_invoices,
                "uploaded": uploaded,
                "processing": processing,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "validation_failed": validation_failed,
                "total_amount": total_amount,
                "pending_amount": pending_amount,
                "approved_amount": approved_amount,
            }
        })
