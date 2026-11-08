
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction

from .models import Invoice
from .serializers import InvoiceSerializer
from .ocr_service import extract_invoice_text, extract_invoice_fields


class InvoiceListCreateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """
        Return all invoices.
        """
        invoices = Invoice.objects.all().order_by("-created_at")

        serializer = InvoiceSerializer(
            invoices,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    def post(self, request):
        """
        Upload an invoice, perform OCR, extract fields,
        check duplicate invoice number, and save the invoice.
        """

        uploaded_file = request.FILES.get("invoice_file")

        # 1. Validate uploaded file
        if not uploaded_file:
            return Response(
                {"error": "Please upload an invoice file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_extensions = [
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".tif",
            ".tiff",
        ]

        file_name = uploaded_file.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            return Response(
                {
                    "error": (
                        "Unsupported file type. "
                        "Upload PDF, PNG, JPG, JPEG, or TIFF."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Validate file size (maximum 10 MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return Response(
                {
                    "error": "File size must be 10 MB or less."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 3. Extract text using OCR
            extracted_text = extract_invoice_text(uploaded_file)

            # 4. Extract invoice fields from OCR text
            invoice_fields = extract_invoice_fields(extracted_text)

            invoice_number = invoice_fields.get("invoice_number")
            vendor_name = invoice_fields.get("vendor_name")

            # 5. Check duplicate invoice number
            duplicate_invoice = False

            if invoice_number:
                duplicate_invoice = Invoice.objects.filter(
                    invoice_number__iexact=invoice_number
                ).exists()

            # 6. Determine validation status
            validation_status = "REVIEW"
            validation_message = (
                "Invoice uploaded successfully. "
                "Please review the extracted information."
            )

            if not extracted_text:
                validation_status = "INVALID"
                validation_message = (
                    "No text could be extracted from the invoice."
                )

            elif duplicate_invoice:
                validation_status = "INVALID"
                validation_message = (
                    "Duplicate invoice number detected."
                )

            elif not invoice_number:
                validation_status = "REVIEW"
                validation_message = (
                    "Invoice number could not be identified."
                )

            elif not invoice_fields.get("total_amount"):
                validation_status = "REVIEW"
                validation_message = (
                    "Invoice total could not be identified."
                )

            else:
                validation_status = "VALID"
                validation_message = (
                    "Invoice fields extracted successfully."
                )

            # 7. Save invoice and extracted information
            with transaction.atomic():
                invoice = Invoice.objects.create(
                    invoice_file=uploaded_file,
                    extracted_text=extracted_text,
                    invoice_number=invoice_number,
                    vendor_name=vendor_name,
                    invoice_date=invoice_fields.get("invoice_date"),
                    due_date=invoice_fields.get("due_date"),
                    total_amount=invoice_fields.get(
                        "total_amount"
                    ) or 0,
                    tax_amount=invoice_fields.get(
                        "tax_amount"
                    ) or 0,
                    status="PENDING",
                    validation_status=validation_status,
                    validation_message=validation_message,
                    is_duplicate=duplicate_invoice,
                )

            # 8. Return invoice data
            serializer = InvoiceSerializer(
                invoice,
                context={"request": request},
            )

            return Response(
                {
                    "message": "Invoice uploaded and OCR completed.",
                    "invoice": serializer.data,
                    "extracted_text": extracted_text,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as error:
            return Response(
                {
                    "error": (
                        "Invoice processing failed: "
                        f"{str(error)}"
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InvoiceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        Return details of one invoice.
        """

        try:
            invoice = Invoice.objects.get(pk=pk)

        except Invoice.DoesNotExist:
            return Response(
                {"error": "Invoice not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = InvoiceSerializer(
            invoice,
            context={"request": request},
        )

        return Response(serializer.data)
