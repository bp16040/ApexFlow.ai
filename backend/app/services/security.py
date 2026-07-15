import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.core.config import get_settings
from app.models.auth import Session as AuthSession
from app.models.auth import User
from app.schemas.auth import TokenPair


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _encode(payload: dict, expires_at: datetime) -> str:
    settings = get_settings()
    return jwt.encode(
        {**payload, "exp": expires_at, "iat": datetime.now(UTC)},
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise ValueError("Unexpected token type")
        return UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc


def issue_tokens(db: DbSession, user: User, *, ip_address: str | None, user_agent: str | None) -> TokenPair:
    settings = get_settings()
    now = datetime.now(UTC)
    refresh_token = secrets.token_urlsafe(48)
    refresh_expiry = now + timedelta(days=settings.refresh_token_days)
    db.add(
        AuthSession(
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            expires_at=refresh_expiry,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    user.last_login_at = now
    db.commit()
    return TokenPair(
        access_token=_encode({"sub": str(user.id), "type": "access"}, now + timedelta(minutes=settings.access_token_minutes)),
        refresh_token=refresh_token,
    )


def rotate_refresh_token(db: DbSession, refresh_token: str, *, ip_address: str | None, user_agent: str | None) -> TokenPair:
    session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_token(refresh_token)))
    if session is None or session.revoked_at is not None or session.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    session.revoked_at = datetime.now(UTC)
    db.flush()
    return issue_tokens(db, user, ip_address=ip_address, user_agent=user_agent)
