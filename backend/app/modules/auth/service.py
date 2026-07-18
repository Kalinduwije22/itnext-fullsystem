import secrets

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserLogin


async def register(db: AsyncSession, data: UserCreate) -> User:
    existing = await db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        phone=data.phone,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate(db: AsyncSession, data: UserLogin) -> str:
    user = await db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return create_access_token(user.id)


async def _fetch_google_tokeninfo(credential: str) -> dict:
    """Isolated so tests can monkeypatch it instead of mocking httpx directly."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo", params={"id_token": credential}
        )
    resp.raise_for_status()
    return resp.json()


async def google_login(db: AsyncSession, credential: str) -> str:
    """Verify a Google Identity Services ID token and find-or-create the user.

    Uses Google's tokeninfo REST endpoint rather than the google-auth package
    — one GET request via httpx (already a dependency) instead of a new
    library, adequate at this app's traffic volume.
    """
    if not settings.google_client_id:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Google sign-in isn't configured")

    try:
        payload = await _fetch_google_tokeninfo(credential)
    except httpx.HTTPStatusError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google credential")

    if payload.get("aud") != settings.google_client_id or payload.get("email_verified") != "true":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google credential")

    email = payload["email"]
    full_name = payload.get("name") or email.split("@")[0]
    user = await db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
        )
        db.add(user)
        await db.flush()
    return create_access_token(user.id)
