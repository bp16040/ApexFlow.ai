from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.auth import User
from app.services.security import issue_tokens


def test_refresh_rotates_session(client: TestClient, db: Session) -> None:
    user = User(email="person@example.edu", full_name="Test Person")
    db.add(user)
    db.commit()
    tokens = issue_tokens(db, user, ip_address=None, user_agent=None)

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens.refresh_token})

    assert response.status_code == 200
    assert response.json()["refresh_token"] != tokens.refresh_token


def test_logout_revokes_refresh_session(client: TestClient, db: Session) -> None:
    user = User(email="logout@example.edu", full_name="Logout User")
    db.add(user)
    db.commit()
    tokens = issue_tokens(db, user, ip_address=None, user_agent=None)

    assert client.post("/api/v1/auth/logout", json={"refresh_token": tokens.refresh_token}).status_code == 204
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens.refresh_token}).status_code == 401
