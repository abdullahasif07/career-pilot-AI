from pathlib import Path

import pytest

from app.services.pdf_parser import extract_text_from_pdf


def test_extract_text_from_corrupt_pdf(tmp_path: Path) -> None:
    pdf = tmp_path / "bad.pdf"
    pdf.write_bytes(b"%PDF-1.4 truncated")

    with pytest.raises(ValueError, match="corrupted"):
        extract_text_from_pdf(pdf)


def test_extract_text_from_valid_pdf(tmp_path: Path) -> None:
    from tests.conftest import MINIMAL_RESUME_PDF

    pdf = tmp_path / "resume.pdf"
    pdf.write_bytes(MINIMAL_RESUME_PDF)

    text = extract_text_from_pdf(pdf)
    assert "Hello Resume" in text
