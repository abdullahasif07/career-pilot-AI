import json

from pydantic import ValidationError

from app.schemas.cover_letter import CoverLetterContent

_BODY_KEYS = (
    "body",
    "cover_letter",
    "letter",
    "text",
    "content",
    "message",
    "coverLetter",
    "cover_letter_body",
)
_SUBJECT_KEYS = ("subject", "subject_line", "email_subject", "title")
_NOTES_KEYS = ("notes", "note", "rationale", "commentary")


def _clean(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _first_long_string(data: dict) -> str | None:
    candidates: list[str] = []
    for value in data.values():
        if isinstance(value, str) and len(value.strip()) > 40:
            candidates.append(value.strip())
        elif isinstance(value, dict):
            nested = parse_cover_letter_content(value)
            return nested.body
    return max(candidates, key=len) if candidates else None


def parse_cover_letter_content(raw: object) -> CoverLetterContent:
    """Normalize model output into CoverLetterContent."""
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("{"):
            try:
                return parse_cover_letter_content(json.loads(text))
            except (json.JSONDecodeError, ValueError):
                pass
        if not text:
            msg = "Model returned an empty cover letter."
            raise ValueError(msg)
        return CoverLetterContent(body=text)

    if not isinstance(raw, dict):
        msg = "Could not parse cover letter from model response."
        raise ValueError(msg)

    try:
        return CoverLetterContent.model_validate(raw)
    except ValidationError:
        pass

    for key in _BODY_KEYS:
        value = raw.get(key)
        if isinstance(value, dict):
            return parse_cover_letter_content(value)

    body = next((_clean(raw.get(key)) for key in _BODY_KEYS if _clean(raw.get(key))), None)
    if body is None:
        body = _first_long_string(raw)

    if not body:
        msg = "Could not parse cover letter from model response."
        raise ValueError(msg)

    subject = next((_clean(raw.get(key)) for key in _SUBJECT_KEYS if _clean(raw.get(key))), None)
    notes = next((_clean(raw.get(key)) for key in _NOTES_KEYS if _clean(raw.get(key))), None)

    return CoverLetterContent(subject=subject, body=body, notes=notes)
