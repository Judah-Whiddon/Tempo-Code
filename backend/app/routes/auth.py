from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.schemas.auth import (
    AuthResponse, LoginRequest, SignupRequest, UserResponse,
)
from app.security import (
    create_access_token, get_current_user, hash_password, verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _synthesize_email(username: str) -> str:
    # The users table still requires email NOT NULL UNIQUE. Auth is username-only
    # by design (Sprint 4), so we mint a deterministic placeholder. If real email
    # collection is ever added, drop this and accept the field at signup.
    return f"{username.lower()}@tempocode.local"


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        username      = payload.username,
        email         = _synthesize_email(payload.username),
        password_hash = hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=create_access_token(user.id),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    # Don't distinguish "wrong username" from "wrong password" — that's a
    # username-enumeration leak. One generic 401 for both paths.
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=create_access_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
