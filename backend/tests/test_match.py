import pytest

from app.schemas.match import JobMatchResult


def test_get_job_match_not_found(client) -> None:
    response = client.get("/jobs/9999/match")
    assert response.status_code == 404


def test_get_job_match_success(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Sierra AI",
            "role": "AI Engineer",
            "raw_description": "Looking for Python and LLM experience with RAG pipelines.",
            "skills": ["Python", "LLMs", "RAG", "Kubernetes"],
            "requirements": ["3+ years Python", "LLM experience"],
        },
    )
    job_id = create.json()["id"]

    client.put(
        "/profile",
        json={
            "name": "Abdullah Asif",
            "summary": "AI engineer with Python, FastAPI, and RAG experience.",
            "projects": [{"title": "CareerPilot AI", "summary": "Built RAG pipeline with Python and FastAPI."}],
        },
    )

    def mock_score(profile, job) -> JobMatchResult:
        return JobMatchResult(
            job_id=job.id,
            overall_score=87,
            strong=["Python", "LLMs", "RAG"],
            missing=["Kubernetes"],
            summary="Strong AI fit; add Kubernetes experience to strengthen the application.",
        )

    monkeypatch.setattr("app.services.match.score_profile_against_job", mock_score)

    response = client.get(f"/jobs/{job_id}/match")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 87
    assert "Python" in data["strong"]
    assert "Kubernetes" in data["missing"]
    assert data["job_id"] == job_id


def test_get_job_match_no_api_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    def raise_no_key(profile, job) -> JobMatchResult:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr("app.services.match.score_profile_against_job", raise_no_key)

    response = client.get(f"/jobs/{job_id}/match")
    assert response.status_code == 503
