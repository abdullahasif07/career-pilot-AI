import pytest

from app.schemas.job import JobParsed, JobStatus


SAMPLE_JD = """
Senior AI Engineer at Sierra AI

We are looking for an AI Engineer to build LLM-powered products.

Requirements:
- 3+ years Python experience
- Experience with RAG and LangChain
- BS in Computer Science or equivalent

Responsibilities:
- Design and ship RAG pipelines
- Collaborate with product team

Skills: Python, FastAPI, PostgreSQL, Kubernetes, AWS
"""


def test_parse_job_description(client, monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_parse(description: str) -> JobParsed:
        return JobParsed(
            company="Sierra AI",
            role="AI Engineer",
            requirements=["3+ years Python experience", "Experience with RAG"],
            skills=["Python", "FastAPI", "Kubernetes", "AWS"],
            responsibilities=["Design and ship RAG pipelines"],
        )

    monkeypatch.setattr("app.services.jobs.parse_job_description", mock_parse)

    response = client.post("/jobs/parse", json={"description": SAMPLE_JD})
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Sierra AI"
    assert data["role"] == "AI Engineer"
    assert "Python" in data["skills"]


def test_job_crud(client) -> None:
    create_payload = {
        "company": "Sierra AI",
        "role": "AI Engineer",
        "raw_description": SAMPLE_JD,
        "status": "interested",
        "requirements": ["Python", "RAG"],
        "skills": ["Python", "FastAPI"],
        "responsibilities": ["Build RAG pipelines"],
        "job_url": "https://example.com/jobs/1",
    }
    create = client.post("/jobs", json=create_payload)
    assert create.status_code == 201
    job_id = create.json()["id"]
    assert create.json()["company"] == "Sierra AI"
    assert create.json()["status"] == "interested"

    get_one = client.get(f"/jobs/{job_id}")
    assert get_one.status_code == 200
    assert get_one.json()["role"] == "AI Engineer"

    list_all = client.get("/jobs")
    assert list_all.status_code == 200
    assert len(list_all.json()) == 1

    update = client.put(
        f"/jobs/{job_id}",
        json={"status": "applied", "company": "Sierra AI Inc."},
    )
    assert update.status_code == 200
    assert update.json()["status"] == "applied"
    assert update.json()["company"] == "Sierra AI Inc."

    delete = client.delete(f"/jobs/{job_id}")
    assert delete.status_code == 204

    missing = client.get(f"/jobs/{job_id}")
    assert missing.status_code == 404


def test_parse_job_requires_min_length(client) -> None:
    response = client.post("/jobs/parse", json={"description": "too short"})
    assert response.status_code == 422


def test_get_job_not_found(client) -> None:
    response = client.get("/jobs/9999")
    assert response.status_code == 404


def test_create_job_defaults_status(client) -> None:
    response = client.post(
        "/jobs",
        json={
            "company": "Acme",
            "role": "Engineer",
            "raw_description": SAMPLE_JD,
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == JobStatus.INTERESTED.value
