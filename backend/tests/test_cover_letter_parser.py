import pytest

from app.agents.cover_letter_parser import parse_cover_letter_content
from app.schemas.cover_letter import CoverLetterContent


def test_parse_standard_shape() -> None:
    result = parse_cover_letter_content(
        {
            "subject": "Application for Engineer",
            "body": "Dear team,\n\nI am a strong fit.",
            "notes": "Emphasized Python.",
        }
    )
    assert result.subject == "Application for Engineer"
    assert "strong fit" in result.body
    assert result.notes == "Emphasized Python."


def test_parse_cover_letter_key() -> None:
    result = parse_cover_letter_content(
        {"cover_letter": "Dear Hiring Manager,\n\nI would love to join.\n\nSincerely,\nAlex"}
    )
    assert result.body.startswith("Dear Hiring Manager")
    assert result.subject is None


def test_parse_plain_text() -> None:
    text = "Dear Acme,\n\nYour mission resonates with me.\n\nBest,\nSam"
    result = parse_cover_letter_content(text)
    assert result.body == text


def test_parse_alternate_keys() -> None:
    result = parse_cover_letter_content(
        {
            "subject_line": "AI Engineer role",
            "letter": "Hello,\n\nHere is my application.",
            "note": "Kept it short.",
        }
    )
    assert result.subject == "AI Engineer role"
    assert "application" in result.body
    assert result.notes == "Kept it short."


def test_parse_nested_cover_letter_object() -> None:
    result = parse_cover_letter_content(
        {
            "cover_letter": {
                "subject": "Hi",
                "body": "Nested body text here.",
            }
        }
    )
    assert result.body == "Nested body text here."


def test_parse_empty_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        parse_cover_letter_content("   ")


def test_generate_falls_back_to_text(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents import cover_letter as cover_letter_agent
    from app.schemas.job import JobRead
    from app.schemas.profile import ProfileRead

    job = JobRead(
        id=1,
        company="Acme",
        role="Engineer",
        status="interested",
        raw_description="Build things.",
        requirements=[],
        skills=[],
        responsibilities=[],
        job_url=None,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )
    profile = ProfileRead(
        id=1,
        name="Alex",
        location=None,
        education=None,
        summary=None,
        linkedin_url=None,
        portfolio_url=None,
        github_url=None,
        projects=[],
        resume=None,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )

    def bad_json(_system: str, _user: str) -> dict:
        return {"cover_letter": "Dear Acme,\n\nPlain letter.\n\nAlex"}

    monkeypatch.setattr(cover_letter_agent, "generate_json", bad_json)
    monkeypatch.setattr(
        cover_letter_agent,
        "generate_text",
        lambda *_args: (_ for _ in ()).throw(AssertionError("should not fallback")),
    )

    result = cover_letter_agent.generate_cover_letter_for_job(profile, job)
    assert "Plain letter" in result.body


def test_generate_uses_text_fallback_when_json_unusable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.agents import cover_letter as cover_letter_agent
    from app.schemas.job import JobRead
    from app.schemas.profile import ProfileRead

    job = JobRead(
        id=1,
        company="Acme",
        role="Engineer",
        status="interested",
        raw_description="Build things.",
        requirements=[],
        skills=[],
        responsibilities=[],
        job_url=None,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )
    profile = ProfileRead(
        id=1,
        name="Alex",
        location=None,
        education=None,
        summary=None,
        linkedin_url=None,
        portfolio_url=None,
        github_url=None,
        projects=[],
        resume=None,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )

    monkeypatch.setattr(
        cover_letter_agent,
        "generate_json",
        lambda *_args: (_ for _ in ()).throw(ValueError("bad json shape")),
    )
    monkeypatch.setattr(
        cover_letter_agent,
        "generate_text",
        lambda *_args: "Dear team,\n\nFreeform cover letter.\n\nAlex",
    )

    result = cover_letter_agent.generate_cover_letter_for_job(profile, job)
    assert "Freeform cover letter" in result.body
