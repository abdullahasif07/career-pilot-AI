import pytest

from app.schemas.resume_extraction import ResumeExtraction


def test_extract_resume_requires_upload(client) -> None:
    response = client.post("/profile/resume/extract")
    assert response.status_code == 400
    assert "Upload" in response.json()["detail"]


def test_extract_resume_success(client, monkeypatch: pytest.MonkeyPatch) -> None:
    client.post(
        "/profile/resume",
        files={"file": ("resume.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    monkeypatch.setattr(
        "app.services.knowledge_base.extract_text_from_pdf",
        lambda _path: "Abdullah Asif\nToronto\nCareerPilot AI project",
    )
    monkeypatch.setattr(
        "app.services.knowledge_base.extract_profile_from_text",
        lambda _text: ResumeExtraction(
            name="Abdullah Asif",
            location="Toronto, ON",
            summary="AI engineer.",
            projects=[{"title": "CareerPilot AI", "summary": "Career copilot app."}],
        ),
    )

    response = client.post("/profile/resume/extract")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Abdullah Asif"
    assert len(data["projects"]) == 1

    # Extraction does not auto-save — profile name still unset until PUT
    profile = client.get("/profile").json()
    assert profile["name"] is None


def test_extract_resume_no_api_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    client.post(
        "/profile/resume",
        files={"file": ("resume.pdf", b"%PDF-1.4 test", "application/pdf")},
    )
    monkeypatch.setattr(
        "app.services.knowledge_base.extract_text_from_pdf",
        lambda _path: "Some resume text",
    )

    def raise_no_key(_text: str) -> ResumeExtraction:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr(
        "app.services.knowledge_base.extract_profile_from_text",
        raise_no_key,
    )

    response = client.post("/profile/resume/extract")
    assert response.status_code == 503
