import pytest

from app.schemas.cover_letter import CoverLetterContent


def test_get_job_cover_letter_not_computed(client) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    response = client.get(f"/jobs/{job_id}/cover-letter")
    assert response.status_code == 200
    data = response.json()
    assert data["computed"] is False
    assert data["cover_letter"] is None


def test_get_job_cover_letter_job_not_found(client) -> None:
    response = client.get("/jobs/9999/cover-letter")
    assert response.status_code == 404


def test_compute_and_get_saved_cover_letter(client, monkeypatch: pytest.MonkeyPatch) -> None:
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

    def mock_generate(profile, job, match=None, tailored_resume=None) -> CoverLetterContent:
        assert profile.name == "Abdullah Asif"
        assert job.company == "Sierra AI"
        return CoverLetterContent(
            subject="Application for AI Engineer — Abdullah Asif",
            body=(
                "Dear Sierra AI team,\n\n"
                "I am excited to apply for the AI Engineer role. "
                "My experience building RAG pipelines with Python aligns well with your needs.\n\n"
                "Sincerely,\nAbdullah Asif"
            ),
            notes="Highlighted Python and RAG experience.",
        )

    monkeypatch.setattr(
        "app.services.cover_letter.generate_cover_letter_for_job",
        mock_generate,
    )

    before = client.get(f"/jobs/{job_id}/cover-letter")
    assert before.json()["computed"] is False

    compute = client.post(f"/jobs/{job_id}/cover-letter/compute")
    assert compute.status_code == 200
    data = compute.json()
    assert data["subject"] == "Application for AI Engineer — Abdullah Asif"
    assert "Sierra AI" in data["body"]
    assert "generated_at" in data

    call_count = {"n": 0}

    def counting_generate(profile, job, match=None, tailored_resume=None) -> CoverLetterContent:
        call_count["n"] += 1
        return mock_generate(profile, job, match, tailored_resume)

    monkeypatch.setattr(
        "app.services.cover_letter.generate_cover_letter_for_job",
        counting_generate,
    )

    cached = client.get(f"/jobs/{job_id}/cover-letter")
    assert cached.status_code == 200
    assert cached.json()["computed"] is True
    assert cached.json()["cover_letter"]["notes"] == "Highlighted Python and RAG experience."
    assert call_count["n"] == 0


def test_compute_job_cover_letter_no_api_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    def raise_no_key(profile, job, match=None, tailored_resume=None) -> CoverLetterContent:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr(
        "app.services.cover_letter.generate_cover_letter_for_job",
        raise_no_key,
    )

    response = client.post(f"/jobs/{job_id}/cover-letter/compute")
    assert response.status_code == 503
