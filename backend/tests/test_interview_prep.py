import pytest

from app.schemas.interview_prep import InterviewPrepContent, InterviewQuestion


def test_get_job_interview_prep_not_computed(client) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    response = client.get(f"/jobs/{job_id}/interview-prep")
    assert response.status_code == 200
    data = response.json()
    assert data["computed"] is False
    assert data["interview_prep"] is None


def test_get_job_interview_prep_job_not_found(client) -> None:
    response = client.get("/jobs/9999/interview-prep")
    assert response.status_code == 404


def test_compute_and_get_saved_interview_prep(client, monkeypatch: pytest.MonkeyPatch) -> None:
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

    def mock_generate(profile, job, match=None, tailored_resume=None) -> InterviewPrepContent:
        assert profile.name == "Abdullah Asif"
        assert job.company == "Sierra AI"
        return InterviewPrepContent(
            questions=[
                InterviewQuestion(
                    question="Explain your RAG architecture.",
                    category="technical",
                    why_likely="Role emphasizes RAG pipelines.",
                    talking_points=["CareerPilot AI project", "Python embeddings"],
                )
            ],
            topics_to_study=["LangGraph", "vector stores"],
            notes="Focus on production LLM deployments.",
        )

    monkeypatch.setattr(
        "app.services.interview_prep.generate_interview_prep_for_job",
        mock_generate,
    )

    before = client.get(f"/jobs/{job_id}/interview-prep")
    assert before.json()["computed"] is False

    compute = client.post(f"/jobs/{job_id}/interview-prep/compute")
    assert compute.status_code == 200
    data = compute.json()
    assert data["questions"][0]["question"] == "Explain your RAG architecture."
    assert data["topics_to_study"] == ["LangGraph", "vector stores"]
    assert "generated_at" in data

    call_count = {"n": 0}

    def counting_generate(profile, job, match=None, tailored_resume=None) -> InterviewPrepContent:
        call_count["n"] += 1
        return mock_generate(profile, job, match, tailored_resume)

    monkeypatch.setattr(
        "app.services.interview_prep.generate_interview_prep_for_job",
        counting_generate,
    )

    cached = client.get(f"/jobs/{job_id}/interview-prep")
    assert cached.status_code == 200
    assert cached.json()["computed"] is True
    assert cached.json()["interview_prep"]["notes"] == "Focus on production LLM deployments."
    assert call_count["n"] == 0


def test_compute_job_interview_prep_no_api_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": "Engineer role with long enough description text here.",
        },
    )
    job_id = create.json()["id"]

    def raise_no_key(profile, job, match=None, tailored_resume=None) -> InterviewPrepContent:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr(
        "app.services.interview_prep.generate_interview_prep_for_job",
        raise_no_key,
    )

    response = client.post(f"/jobs/{job_id}/interview-prep/compute")
    assert response.status_code == 503
