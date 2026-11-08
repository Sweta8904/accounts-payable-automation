
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


def clean_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip(" :\t-")


def find_first(patterns, text, flags=re.IGNORECASE):
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return clean_text(match.group(1))
    return None


def parse_date(value):
    if not value:
        return None

    value = value.strip()
    formats = [
        "%d/%m/%Y", "%d-%m-%Y",
        "%Y-%m-%d", "%d.%m.%Y",
        "%d/%m/%y", "%d-%m-%y",
        "%d %b %Y", "%d %B %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def parse_amount(value):
    if not value:
        return None

    # Handles values such as ₹15,000.00, INR 15000.00 and 15,000
    cleaned = re.sub(r"[^\d.,\-]", "", value)
    if not cleaned:
        return None

    # Treat the final comma/dot followed by 1-2 digits as decimals.
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(".") > cleaned.rfind(","):
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) in (1, 2):
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        else:
            cleaned = "".join(parts)

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def extract_invoice_fields(raw_text):
    text = raw_text or ""

    invoice_number = find_first([
        r"(?:invoice\s*(?:number|no|#|num)|bill\s*(?:number|no|#))\s*[:#\-]?\s*([A-Z0-9][A-Z0-9/\-_]+)",
        r"\b(INV[-/][A-Z0-9/\-_]+)\b",
    ], text)

    invoice_date_text = find_first([
        r"(?:invoice\s*date|bill\s*date|date\s*of\s*invoice)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
    ], text)

    due_date_text = find_first([
        r"(?:due\s*date|payment\s*due)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
    ], text)

    vendor_name = find_first([
        r"(?:vendor\s*name|supplier\s*name|seller\s*name)\s*[:\-]\s*([^\n]+)",
        r"(?:from)\s*[:\-]\s*([^\n]+)",
    ], text)

    total_text = find_first([
        r"(?:grand\s*total|total\s*amount|invoice\s*total|amount\s*due|net\s*payable|total)\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    ], text)

    tax_text = find_first([
        r"(?:total\s*GST|GST\s*amount|tax\s*amount|total\s*tax|IGST|CGST|SGST)\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    ], text)

    subtotal_text = find_first([
        r"(?:subtotal|sub\s*total|taxable\s*amount)\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    ], text)

    return {
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "invoice_date": parse_date(invoice_date_text),
        "due_date": parse_date(due_date_text),
        "total_amount": parse_amount(total_text),
        "tax_amount": parse_amount(tax_text),
        "subtotal_amount": parse_amount(subtotal_text),
        "currency": "INR",
    }
