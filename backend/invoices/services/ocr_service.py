
from pathlib import Path
from io import BytesIO

import pymupdf
import pytesseract

from PIL import Image
from django.conf import settings


# Configure Windows Tesseract executable
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def extract_text_from_image(image):
    """Extract text from a JPG or PNG image."""
    image = image.convert("RGB")

    return pytesseract.image_to_string(
        image,
        lang="eng",
        config="--oem 3 --psm 6"
    )


def extract_text_from_pdf(file_path):
    """Extract digital PDF text and OCR scanned PDF pages."""
    extracted_pages = []

    document = pymupdf.open(file_path)

    try:
        for page_number, page in enumerate(document):
            text = page.get_text("text").strip()

            # OCR pages that contain little or no selectable text
            if len(text) < 30:
                pixmap = page.get_pixmap(
                    dpi=200,
                    colorspace=pymupdf.csRGB,
                    alpha=False
                )

                image_bytes = pixmap.tobytes("png")
                image = Image.open(BytesIO(image_bytes))

                text = extract_text_from_image(image).strip()

            extracted_pages.append(
                f"--- Page {page_number + 1} ---\n{text}"
            )

    finally:
        document.close()

    return "\n\n".join(extracted_pages).strip()


def extract_invoice_text(file_path):
    """Automatically identify PDF or image and extract text."""
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in [".jpg", ".jpeg", ".png"]:
        with Image.open(file_path) as image:
            return extract_text_from_image(image).strip()

    raise ValueError("Unsupported invoice file format.")
