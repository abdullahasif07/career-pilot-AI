import pytest


def test_get_knowledge_summary_empty(client) -> None:
    response = client.get("/profile/knowledge-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["has_summary"] is False
    assert data["summary"] is None


def test_get_knowledge_summary_prompt_default(client) -> None:
    response = client.get("/profile/knowledge-summary/prompt")
    assert response.status_code == 200
    data = response.json()
    assert "knowledge base summary" in data["default_system_prompt"].lower()
    assert data["uses_custom"] is False


def test_update_knowledge_summary_manually(client) -> None:
    update = client.put(
        "/profile/knowledge-summary",
        json={"summary": "AI engineer with Python and RAG experience."},
    )
    assert update.status_code == 200
    assert update.json()["has_summary"] is True

    get = client.get("/profile/knowledge-summary")
    assert get.json()["summary"] == "AI engineer with Python and RAG experience."


def test_compute_knowledge_summary_requires_profile_data(client) -> None:
    response = client.post("/profile/knowledge-summary/compute")
    assert response.status_code == 400
    assert "profile details" in response.json()["detail"].lower()


def test_compute_and_save_knowledge_summary(client, monkeypatch: pytest.MonkeyPatch) -> None:
    client.put(
        "/profile",
        json={
            "name": "Abdullah Asif",
            "summary": "AI engineer with Python experience.",
            "projects": [{"title": "CareerPilot AI", "summary": "RAG copilot app."}],
        },
    )

    def mock_summarize(profile, resume_text=None, system_prompt=None) -> str:
        assert profile.name == "Abdullah Asif"
        return (
            "The candidate is an AI engineer with Python and RAG experience. "
            "Notable project: CareerPilot AI."
        )

    monkeypatch.setattr(
        "app.services.knowledge_base.summarize_knowledge_base",
        mock_summarize,
    )

    compute = client.post("/profile/knowledge-summary/compute")
    assert compute.status_code == 200
    assert "CareerPilot AI" in compute.json()["summary"]

    cached = client.get("/profile/knowledge-summary")
    assert cached.json()["has_summary"] is True

    profile = client.get("/profile").json()
    assert profile["agent_knowledge_summary"] is not None


def test_custom_knowledge_summary_prompt_used(client, monkeypatch: pytest.MonkeyPatch) -> None:
    custom = "Write a one-paragraph agent briefing in plain text."

    client.put("/profile/knowledge-summary/prompt", json={"system_prompt": custom})
    client.put("/profile", json={"name": "Alex", "summary": "Backend developer."})

    captured: dict[str, str | None] = {"prompt": None}

    def mock_summarize(profile, resume_text=None, system_prompt=None) -> str:
        captured["prompt"] = system_prompt
        return "Alex is a backend developer."

    monkeypatch.setattr(
        "app.services.knowledge_base.summarize_knowledge_base",
        mock_summarize,
    )

    response = client.post("/profile/knowledge-summary/compute")
    assert response.status_code == 200
    assert captured["prompt"] == custom


def test_format_profile_uses_agent_summary() -> None:
    from datetime import UTC, datetime

    from app.prompts.formatters import format_profile
    from app.schemas.profile import ProfileRead

    profile = ProfileRead(
        id=1,
        name="Alex",
        location=None,
        education=None,
        summary="Short profile summary.",
        linkedin_url=None,
        portfolio_url=None,
        github_url=None,
        projects=[],
        resume=None,
        agent_knowledge_summary="Full agent-ready knowledge base summary here.",
        agent_knowledge_summary_generated_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    formatted = format_profile(profile, empty_message="empty")
    assert formatted == "Full agent-ready knowledge base summary here."
