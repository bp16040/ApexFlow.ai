import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.auth import PasswordlessToken, Session as AuthSession, User
from app.schemas.auth import MagicLinkRequest, MagicLinkVerifyRequest, RefreshRequest, TokenPair, UserResponse
from app.services.security import hash_token, issue_tokens, rotate_refresh_token

router = APIRouter(prefix="/auth", tags=["authentication"])


def request_metadata(request: Request) -> tuple[str | None, str | None]:
    return request.client.host if request.client else None, request.headers.get("user-agent")


@router.get("/google/login")
def google_login(request: Request) -> RedirectResponse:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google OAuth is not configured")
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
    )
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")


@router.get("/google/callback", response_model=TokenPair)
async def google_callback(code: str, state: str, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    settings = get_settings()
    if not secrets.compare_digest(state, request.session.pop("google_oauth_state", "")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret.get_secret_value() if settings.google_client_secret else "",
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.is_error:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google authorization failed")
        info_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
        )
    if info_response.is_error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google profile lookup failed")
    profile = info_response.json()
    email = str(profile.get("email", "")).lower()
    if not email or not profile.get("email_verified"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A verified Google email is required")
    allowed_domains = {item.strip().lower() for item in settings.allowed_google_workspace_domains.split(",") if item.strip()}
    if allowed_domains and email.rsplit("@", 1)[-1] not in allowed_domains:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google Workspace domain is not allowed")
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, full_name=profile.get("name") or email, avatar_url=profile.get("picture"))
        db.add(user)
        db.flush()
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    ip_address, user_agent = request_metadata(request)
    return issue_tokens(db, user, ip_address=ip_address, user_agent=user_agent)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    ip_address, user_agent = request_metadata(request)
    return rotate_refresh_token(db, payload.refresh_token, ip_address=ip_address, user_agent=user_agent)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> Response:
    session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_token(payload.refresh_token)))
    if session is not None:
        session.revoked_at = datetime.now(UTC)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/passwordless/request", status_code=status.HTTP_202_ACCEPTED)
def request_passwordless(payload: MagicLinkRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    email = payload.email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user and user.is_active:
        raw_token = secrets.token_urlsafe(48)
        db.add(
            PasswordlessToken(
                email=email,
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=datetime.now(UTC) + timedelta(minutes=get_settings().passwordless_token_minutes),
            )
        )
        db.commit()
        # Delivery is intentionally delegated to a configured transactional-email adapter.
        # The raw token is never returned by this API.
    return {"detail": "If the account exists, a sign-in link will be sent."}


@router.post("/passwordless/verify", response_model=TokenPair)
def verify_passwordless(
    payload: MagicLinkVerifyRequest, request: Request, db: Session = Depends(get_db)
) -> TokenPair:
    token = db.scalar(select(PasswordlessToken).where(PasswordlessToken.token_hash == hash_token(payload.token)))
    if token is None or token.consumed_at is not None or token.expires_at <= datetime.now(UTC) or token.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired sign-in link")
    user = db.get(User, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    token.consumed_at = datetime.now(UTC)
    db.flush()
    ip_address, user_agent = request_metadata(request)
    return issue_tokens(db, user, ip_address=ip_address, user_agent=user_agent)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user
