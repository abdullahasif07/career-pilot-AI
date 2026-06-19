import pytest

from app.agents.interview_prep_parser import parse_interview_prep_content
from app.schemas.interview_prep import InterviewPrepContent, InterviewQuestion


def test_parse_canonical_shape() -> None:
    result = parse_interview_prep_content(
        {
            "questions": [
                {
                    "question": "Explain your RAG architecture.",
                    "category": "technical",
                    "why_likely": "Role emphasizes RAG pipelines.",
                    "talking_points": ["CareerPilot AI", "Python embeddings"],
                }
            ],
            "topics_to_study": ["LangGraph", "vector stores"],
            "notes": "Focus on production deployments.",
        }
    )
    assert result.questions[0].question == "Explain your RAG architecture."
    assert result.topics_to_study == ["LangGraph", "vector stores"]
    assert result.notes == "Focus on production deployments."


def test_parse_alternate_question_keys() -> None:
    result = parse_interview_prep_content(
        {
            "likely_questions": [
                {
                    "text": "Why LangGraph?",
                    "type": "technical",
                    "reason": "Job mentions agent orchestration.",
                    "hints": ["Compared alternatives", "Used in CareerPilot AI"],
                }
            ],
            "study_topics": ["Agent frameworks"],
        }
    )
    assert result.questions[0].question == "Why LangGraph?"
    assert result.questions[0].category == "technical"
    assert result.questions[0].talking_points == ["Compared alternatives", "Used in CareerPilot AI"]
    assert result.topics_to_study == ["Agent frameworks"]


def test_parse_list_of_strings() -> None:
    result = parse_interview_prep_content(
        ["Explain your RAG architecture.", "Why did you choose Python?"]
    )
    assert len(result.questions) == 2
    assert result.questions[0].question == "Explain your RAG architecture."


def test_parse_plain_text_fallback() -> None:
    result = parse_interview_prep_content("Tell me about a challenging LLM deployment.")
    assert result.questions[0].question == "Tell me about a challenging LLM deployment."


def test_parse_empty_raises() -> None:
    with pytest.raises(ValueError, match="empty interview prep"):
        parse_interview_prep_content("   ")


def test_agent_falls_back_to_text(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents import interview_prep as interview_prep_agent
    from app.schemas.job import JobRead
    from app.schemas.profile import ProfileRead

    job = JobRead(
        id=1,
        company="Sierra AI",
        role="AI Engineer",
        status="interested",
        raw_description="Build LLM products.",
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
        summary="AI engineer",
        linkedin_url=None,
        portfolio_url=None,
        github_url=None,
        projects=[],
        resume=None,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )

    def bad_json(*_args, **_kwargs) -> dict:
        raise ValueError("bad json")

    monkeypatch.setattr(interview_prep_agent, "generate_json", bad_json)
    monkeypatch.setattr(
        interview_prep_agent,
        "generate_text",
        lambda *_args: '{"questions": [{"question": "Walk me through your RAG pipeline."}]}',
    )

    result = interview_prep_agent.generate_interview_prep_for_job(profile, job)
    assert "RAG pipeline" in result.questions[0].question
