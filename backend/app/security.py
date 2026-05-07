"""
Password hashing + JWT helpers + the FastAPI auth dependency.

Decisions (locked in archive/sprint-4-plan.md):
  - bcrypt via passlib for password hashing.
  - HS256 JWTs, 7-day expiry, signed with $JWT_SECRET from the environment.
  - Tokens carry the user UUID in `sub` (stringified). The frontend never
    trusts claims directly — it always re-fetches via /auth/me.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User


# ── Config ────────────────────────────────────────────────────────────────────

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 7

# passlib pins bcrypt rounds via the context. Default cost (~12) is fine —
# ~200ms/hash is the *point* of bcrypt, don't tune it down.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        # Fail loud at first use rather than silently signing with "" — a missing
        # secret in prod is a security incident, not a soft fallback.
        raise RuntimeError("JWT_SECRET is not set in the environment")
    return secret


# ── Passwords ─────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── Tokens ────────────────────────────────────────────────────────────────────

def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=JWT_EXPIRY_DAYS)).timestamp()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return UUID(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.split(" ", 1)[1].strip()
    user_id = decode_access_token(token)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    """Like get_current_user, but returns None instead of raising 401 when the
    request is unauthenticated. For endpoints that work for anonymous users
    (submissions, etc.) where login enriches the experience but isn't required."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    try:
        user_id = decode_access_token(token)
    except HTTPException:
        # Token present but invalid/expired — treat as anonymous instead of
        # rejecting. The frontend AuthContext clears bad tokens on its own.
        return None
    return db.query(User).filter(User.id == user_id).first()
