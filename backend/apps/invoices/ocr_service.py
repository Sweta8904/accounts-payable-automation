
import io

import fitz
import pytesseract
from PIL import Image

import re
from datetime import datetime
from decimal import Decimal

# Windows: update this path if Tesseract is installed elsewhere.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_invoice_text(uploaded_file):
    """
    Extract text from a PDF or image invoice.
    Supports PDF, PNG, JPG, JPEG, and TIFF.
    """
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    extracted_text = ""

    if file_name.endswith(".pdf"):
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")

        for page in pdf_document:
            # First try extracting text directly from the PDF.
            page_text = page.get_text().strip()

            # If the PDF is scanned, use OCR.
            if not page_text:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )
                page_text = pytesseract.image_to_string(image)

            extracted_text += page_text + "\n"

        pdf_document.close()

    else:
        image = Image.open(io.BytesIO(file_bytes))
        extracted_text = pytesseract.image_to_string(image)

    return extracted_text.strip()

def extract_invoice_fields(text):
    """
    Extract common invoice fields from OCR text.
    This is rule-based extraction, not AI.
    """

    fields = {
        "invoice_number": None,
        "vendor_name": None,
        "invoice_date": None,
        "due_date": None,
        "total_amount": Decimal("0.00"),
        "tax_amount": Decimal("0.00"),
    }

    # Invoice number
    invoice_match = re.search(
        r"(?:invoice\s*(?:no|number|#)|inv\s*#?)\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        text,
        re.IGNORECASE,
    )

    if invoice_match:
        fields["invoice_number"] = invoice_match.group(1)

    # Invoice date
    date_match = re.search(
        r"(?:invoice\s*date|date)\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        text,
        re.IGNORECASE,
    )

    if date_match:
        fields["invoice_date"] = parse_date(date_match.group(1))

    # Due date
    due_match = re.search(
        r"due\s*date\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        text,
        re.IGNORECASE,
    )

    if due_match:
        fields["due_date"] = parse_date(due_match.group(1))

    # Tax amount
    tax_match = re.search(
        r"(?:tax|gst|vat|total\s*tax)\s*[:\-]?\s*"
        r"(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE,
    )

    if tax_match:
        fields["tax_amount"] = Decimal(
            tax_match.group(1).replace(",", "")
        )

    # Total amount
    total_match = re.search(
        r"(?:grand\s*total|total\s*amount|invoice\s*total|amount\s*due)"
        r"\s*[:\-]?\s*(?:₹|rs\.?|inr)?\s*"
        r"([\d,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE,
    )

    if total_match:
        fields["total_amount"] = Decimal(
            total_match.group(1).replace(",", "")
        )

    return fields


def parse_date(value):
    for date_format in (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    return None
