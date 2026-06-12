import pytest

from app.schemas.tailored_resume import TailoredResumeContent, TailoredResumeSection


def test_get_job_tailored_resume_not_computed(client) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    response = client.get(f"/jobs/{job_id}/resume/tailor")
    assert response.status_code == 200
    data = response.json()
    assert data["computed"] is False
    assert data["resume"] is None


def test_get_job_tailored_resume_job_not_found(client) -> None:
    response = client.get("/jobs/9999/resume/tailor")
    assert response.status_code == 404


def test_compute_tailored_resume_requires_master_resume(client) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    response = client.post(f"/jobs/{job_id}/resume/tailor/compute")
    assert response.status_code == 400
    assert "Upload a master resume" in response.json()["detail"]


def test_compute_and_get_saved_tailored_resume(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Sierra AI",
            "role": "AI Engineer",
            "raw_description": "Looking for Python and LLM experience with RAG pipelines.",
            "skills": ["Python", "LLMs", "RAG"],
        },
    )
    job_id = create.json()["id"]

    client.put(
        "/profile",
        json={
            "name": "Abdullah Asif",
            "summary": "AI engineer with Python and RAG experience.",
            "projects": [{"title": "CareerPilot AI", "summary": "Built RAG pipeline with Python."}],
        },
    )

    def mock_tailor(master_resume_text, profile, job, match=None) -> TailoredResumeContent:
        assert "Python developer" in master_resume_text
        assert job.company == "Sierra AI"
        return TailoredResumeContent(
            summary="AI engineer focused on Python and RAG systems.",
            sections=[
                TailoredResumeSection(
                    heading="Experience",
                    items=[
                        {
                            "title": "Software Engineer",
                            "bullets": [
                                "Built AI-powered systems with Python and RAG pipelines.",
                            ],
                        }
                    ],
                )
            ],
            notes="Emphasized Python and RAG experience.",
        )

    monkeypatch.setattr(
        "app.services.resume_tailor.knowledge_base.get_master_resume_text",
        lambda db: "Python developer with FastAPI experience.",
    )
    monkeypatch.setattr("app.services.resume_tailor.tailor_resume_for_job", mock_tailor)

    before = client.get(f"/jobs/{job_id}/resume/tailor")
    assert before.json()["computed"] is False

    compute = client.post(f"/jobs/{job_id}/resume/tailor/compute")
    assert compute.status_code == 200
    data = compute.json()
    assert data["summary"] == "AI engineer focused on Python and RAG systems."
    assert data["sections"][0]["heading"] == "Experience"
    assert "generated_at" in data

    call_count = {"n": 0}

    def counting_tailor(master_resume_text, profile, job, match=None) -> TailoredResumeContent:
        call_count["n"] += 1
        return mock_tailor(master_resume_text, profile, job, match)

    monkeypatch.setattr("app.services.resume_tailor.tailor_resume_for_job", counting_tailor)

    cached = client.get(f"/jobs/{job_id}/resume/tailor")
    assert cached.status_code == 200
    assert cached.json()["computed"] is True
    assert cached.json()["resume"]["notes"] == "Emphasized Python and RAG experience."
    assert call_count["n"] == 0


def test_compute_job_tailored_resume_no_api_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    monkeypatch.setattr(
        "app.services.resume_tailor.knowledge_base.get_master_resume_text",
        lambda db: "Resume text here.",
    )

    def raise_no_key(master_resume_text, profile, job, match=None) -> TailoredResumeContent:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr("app.services.resume_tailor.tailor_resume_for_job", raise_no_key)

    response = client.post(f"/jobs/{job_id}/resume/tailor/compute")
    assert response.status_code == 503
