from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

_CORRUPT_PDF_MSG = (
    "Could not read this PDF — the file may be corrupted or incomplete. "
    "Re-upload your master resume from the Knowledge Base page."
)


def extract_text_from_pdf(path: Path) -> str:
    if not path.exists():
        msg = "Resume file not found."
        raise ValueError(msg)

    try:
        reader = PdfReader(str(path), strict=False)
    except (PdfReadError, PdfStreamError, OSError, ValueError) as exc:
        raise ValueError(_CORRUPT_PDF_MSG) from exc

    if len(reader.pages) == 0:
        msg = "This PDF has no pages. Re-upload a valid resume PDF."
        raise ValueError(msg)

    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    text = "\n".join(pages).strip()

    if not text:
        msg = (
            "Could not read text from this PDF. "
            "Use a text-based resume (not a scanned image), then upload again."
        )
        raise ValueError(msg)

    return text
