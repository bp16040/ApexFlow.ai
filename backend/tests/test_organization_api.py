from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.auth import User
from app.services.security import issue_tokens


def test_superuser_can_create_organization(client: TestClient, db: Session) -> None:
    admin = User(email="admin@example.edu", full_name="Admin", is_superuser=True)
    db.add(admin)
    db.commit()
    tokens = issue_tokens(db, admin, ip_address=None, user_agent=None)

    response = client.post(
        "/api/v1/organization/organizations",
        headers={"Authorization": f"Bearer {tokens.access_token}"},
        json={"name": "Apex Institute", "slug": "apex-institute"},
    )

    assert response.status_code == 201
    assert "id" in response.json()


def test_organization_guard_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/organization/organizations")

    assert response.status_code == 401
