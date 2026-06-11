from datetime import UTC, datetime

import pytest

from app.schemas.match import JobMatchResult, JobMatchScore


def test_get_job_match_not_computed(client) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    response = client.get(f"/jobs/{job_id}/match")
    assert response.status_code == 200
    data = response.json()
    assert data["computed"] is False
    assert data["match"] is None


def test_get_job_match_job_not_found(client) -> None:
    response = client.get("/jobs/9999/match")
    assert response.status_code == 404


def test_compute_and_get_saved_match(client, monkeypatch: pytest.MonkeyPatch) -> None:
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

    def mock_score(profile, job) -> JobMatchScore:
        return JobMatchScore(
            overall_score=87,
            strong=["Python", "LLMs", "RAG"],
            missing=["Kubernetes"],
            summary="Strong AI fit.",
        )

    monkeypatch.setattr("app.services.match.score_profile_against_job", mock_score)

    # GET before compute — not saved yet
    before = client.get(f"/jobs/{job_id}/match")
    assert before.json()["computed"] is False

    compute = client.post(f"/jobs/{job_id}/match/compute")
    assert compute.status_code == 200
    assert compute.json()["overall_score"] == 87

    # GET returns cached score without calling Gemini again
    call_count = {"n": 0}

    def counting_score(profile, job) -> JobMatchScore:
        call_count["n"] += 1
        return mock_score(profile, job)

    monkeypatch.setattr("app.services.match.score_profile_against_job", counting_score)

    cached = client.get(f"/jobs/{job_id}/match")
    assert cached.status_code == 200
    assert cached.json()["computed"] is True
    assert cached.json()["match"]["overall_score"] == 87
    assert call_count["n"] == 0


def test_compute_job_match_no_api_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    def raise_no_key(profile, job) -> JobMatchScore:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr("app.services.match.score_profile_against_job", raise_no_key)

    response = client.post(f"/jobs/{job_id}/match/compute")
    assert response.status_code == 503
