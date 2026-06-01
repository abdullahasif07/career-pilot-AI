def test_get_profile_returns_defaults(client) -> None:
    response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] is None
    assert "created_at" in data
    assert "updated_at" in data


def test_update_profile_persists(client) -> None:
    payload = {
        "name": "Abdullah Asif",
        "location": "Toronto, ON",
        "education": "BSc Computer Science",
        "linkedin_url": "https://linkedin.com/in/abdullahasif07",
        "portfolio_url": "https://example.com",
        "github_url": "https://github.com/abdullahasif07",
    }
    response = client.put("/profile", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]
    assert response.json()["github_url"] == payload["github_url"]

    get_response = client.get("/profile")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == payload["name"]
    assert get_response.json()["location"] == payload["location"]


def test_partial_update_preserves_other_fields(client) -> None:
    client.put(
        "/profile",
        json={"name": "Abdullah", "location": "Canada"},
    )
    response = client.put("/profile", json={"github_url": "https://github.com/abdullahasif07"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Abdullah"
    assert data["location"] == "Canada"
    assert data["github_url"] == "https://github.com/abdullahasif07"
