from PyPDF2 import PdfReader

from app.core.errors import PdfProcessingError


def _cleanup_text(raw_text: str) -> str:
    cleaned = raw_text.replace("\x00", " ").replace("\ufeff", " ")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF with fallback handling for partially broken pages."""
    try:
        reader = PdfReader(file_path)
    except Exception as exc:
        raise PdfProcessingError("Invalid or corrupted PDF file.") from exc

    pages_text: list[str] = []
    for page in reader.pages:
        try:
            extracted = page.extract_text() or ""
        except Exception:
            extracted = ""
        normalized = _cleanup_text(extracted)
        if normalized:
            pages_text.append(normalized)

    if not pages_text:
        raise PdfProcessingError("Could not extract readable text from the PDF CV.")

    return "\n".join(pages_text)
