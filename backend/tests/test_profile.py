def test_get_profile_returns_defaults(client) -> None:
    response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] is None
    assert data["summary"] is None
    assert data["projects"] == []
    assert data["resume"] is None
    assert "created_at" in data


def test_update_profile_with_summary_and_projects(client) -> None:
    payload = {
        "name": "Abdullah Asif",
        "summary": "AI engineer focused on LLM systems and RAG pipelines.",
        "projects": [
            {"title": "CareerPilot AI", "summary": "Full-stack career copilot with FastAPI."},
            {"title": "Auction Platform", "summary": "Real-time MERN auction app."},
        ],
    }
    response = client.put("/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == payload["summary"]
    assert len(data["projects"]) == 2
    assert data["projects"][0]["title"] == "CareerPilot AI"

    get_response = client.get("/profile")
    assert get_response.json()["projects"][1]["title"] == "Auction Platform"


def test_partial_update_preserves_projects(client) -> None:
    client.put(
        "/profile",
        json={
            "name": "Abdullah",
            "projects": [{"title": "Project A", "summary": "First"}],
        },
    )
    response = client.put("/profile", json={"github_url": "https://github.com/abdullahasif07"})
    data = response.json()
    assert data["name"] == "Abdullah"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "Project A"


def test_upload_and_delete_resume(client) -> None:
    pdf_bytes = b"%PDF-1.4 minimal test resume"
    upload = client.post(
        "/profile/resume",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200
    assert upload.json()["resume"]["filename"] == "resume.pdf"

    delete = client.delete("/profile/resume")
    assert delete.status_code == 200
    assert delete.json()["resume"] is None


def test_upload_resume_rejects_non_pdf(client) -> None:
    response = client.post(
        "/profile/resume",
        files={"file": ("resume.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
