import json

from pydantic import ValidationError

from app.schemas.interview_prep import InterviewPrepContent, InterviewQuestion

_QUESTIONS_KEYS = (
    "questions",
    "interview_questions",
    "likely_questions",
    "prep_questions",
)
_TOPICS_KEYS = ("topics_to_study", "topics", "study_topics", "areas_to_study")
_NOTES_KEYS = ("notes", "note", "summary", "strategy")


def _clean(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_question(raw: object) -> InterviewQuestion | None:
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        return InterviewQuestion(question=text)

    if not isinstance(raw, dict):
        return None

    try:
        return InterviewQuestion.model_validate(raw)
    except ValidationError:
        pass

    question = next(
        (
            _clean(raw.get(key))
            for key in ("question", "text", "prompt", "q", "title")
            if _clean(raw.get(key))
        ),
        None,
    )
    if question is None:
        return None

    category = next(
        (
            _clean(raw.get(key))
            for key in ("category", "type", "topic", "kind")
            if _clean(raw.get(key))
        ),
        None,
    )
    why_likely = next(
        (
            _clean(raw.get(key))
            for key in ("why_likely", "reason", "rationale", "why")
            if _clean(raw.get(key))
        ),
        None,
    )

    talking_points: list[str] = []
    for key in ("talking_points", "talkingPoints", "hints", "prep_points", "points"):
        value = raw.get(key)
        if isinstance(value, list):
            talking_points = [item.strip() for item in value if isinstance(item, str) and item.strip()]
            if talking_points:
                break

    return InterviewQuestion(
        question=question,
        category=category,
        why_likely=why_likely,
        talking_points=talking_points,
    )


def _parse_questions(raw: object) -> list[InterviewQuestion]:
    if isinstance(raw, list):
        questions = [_parse_question(item) for item in raw]
        return [question for question in questions if question is not None]

    if isinstance(raw, dict):
        for key in _QUESTIONS_KEYS:
            if key in raw:
                return _parse_questions(raw[key])

    return []


def _parse_topics(raw: dict) -> list[str]:
    for key in _TOPICS_KEYS:
        value = raw.get(key)
        if isinstance(value, list):
            topics = [item.strip() for item in value if isinstance(item, str) and item.strip()]
            if topics:
                return topics
    return []


def parse_interview_prep_content(raw: object) -> InterviewPrepContent:
    """Normalize model output into InterviewPrepContent."""
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("{"):
            try:
                return parse_interview_prep_content(json.loads(text))
            except (json.JSONDecodeError, ValueError):
                pass
        if not text:
            msg = "Model returned empty interview prep."
            raise ValueError(msg)
        return InterviewPrepContent(questions=[InterviewQuestion(question=text)])

    if isinstance(raw, list):
        questions = _parse_questions(raw)
        if not questions:
            msg = "Could not parse interview prep from model response."
            raise ValueError(msg)
        return InterviewPrepContent(questions=questions)

    if not isinstance(raw, dict):
        msg = "Could not parse interview prep from model response."
        raise ValueError(msg)

    for key in _QUESTIONS_KEYS:
        nested = raw.get(key)
        if isinstance(nested, dict):
            return parse_interview_prep_content(nested)

    try:
        return InterviewPrepContent.model_validate(raw)
    except ValidationError:
        pass

    questions = _parse_questions(raw)
    if not questions:
        msg = "Could not parse interview prep from model response."
        raise ValueError(msg)

    notes = next((_clean(raw.get(key)) for key in _NOTES_KEYS if _clean(raw.get(key))), None)

    return InterviewPrepContent(
        questions=questions,
        topics_to_study=_parse_topics(raw),
        notes=notes,
    )
