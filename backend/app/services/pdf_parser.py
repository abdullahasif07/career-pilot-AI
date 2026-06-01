from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(path: Path) -> str:
    if not path.exists():
        msg = "Resume file not found."
        raise ValueError(msg)

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()

    if not text:
        msg = "Could not read text from this PDF. Try a text-based resume (not a scanned image)."
        raise ValueError(msg)

    return text
