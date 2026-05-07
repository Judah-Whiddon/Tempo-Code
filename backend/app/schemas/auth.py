"""Auth request/response schemas. Username + password only — email is
synthesized server-side because the users table still requires it (NOT NULL,
UNIQUE), but we don't surface email at signup per the Sprint 4 scope."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id:           UUID
    username:     str
    streak_count: int
    created_at:   datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user:         UserResponse
    access_token: str
