"""Auth schemas."""
from __future__ import annotations

from pydantic import BaseModel


class TelegramLoginRequest(BaseModel):
    init_data: str


class School21LoginRequest(BaseModel):
    init_data: str
    login: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    onboarding_done: bool
