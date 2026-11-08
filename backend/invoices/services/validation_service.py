
from .extraction_service import extract_invoice_fields


def validate_invoice(invoice):
    errors = []

    if not invoice.invoice_number:
        errors.append("Invoice number is missing.")

    if not invoice.vendor_name:
        errors.append("Vendor name is missing.")

    if not invoice.invoice_date:
        errors.append("Invoice date is missing.")

    if not invoice.total_amount or invoice.total_amount <= 0:
        errors.append("Total amount must be greater than zero.")

    # Check whether another invoice has the same vendor and invoice number.
    from invoices.models import Invoice

    duplicates = Invoice.objects.filter(
        invoice_number__iexact=invoice.invoice_number or "",
        vendor_name__iexact=invoice.vendor_name or "",
    ).exclude(pk=invoice.pk)

    is_duplicate = duplicates.exists()

    if is_duplicate:
        errors.append("Duplicate invoice: this vendor and invoice number already exist.")

    invoice.is_duplicate = is_duplicate
    invoice.validation_message = "\n".join(errors) if errors else "All basic validations passed."
    invoice.validation_status = "FAILED" if errors else "VALID"
    invoice.save(update_fields=[
        "is_duplicate",
        "validation_message",
        "validation_status",
        "updated_at",
    ])

    return {
        "valid": not errors,
        "is_duplicate": is_duplicate,
        "errors": errors,
    }
