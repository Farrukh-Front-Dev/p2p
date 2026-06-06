"""API so'rov/javob sxemalari (Pydantic)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ---- Auth ----


class AuthRequest(BaseModel):
    init_data: str = Field(..., description="Telegram WebApp initData satri")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool
    user: UserOut


# ---- User ----


class UserOut(BaseModel):
    id: int
    username: str | None = None
    nickname: str | None = None
    school21_login: str | None = None
    language: str
    directions: list[str]
    coins: int
    max_coins: int
    xp: int
    level: int
    level_name: str
    level_progress: int
    xp_to_next: int
    rating: float
    total_taught: int
    total_learned: int


class RegisterRequest(BaseModel):
    """Ro'yxatdan o'tishni yakunlash (School 21 login + parol + yo'nalishlar)."""

    school21_login: str
    school21_password: str
    directions: list[str] = Field(default_factory=list, max_length=5)
    language: str = "uz"


class UpdateProfileRequest(BaseModel):
    language: str | None = None
    directions: list[str] | None = Field(default=None, max_length=5)


# ---- Slot ----


class SlotOut(BaseModel):
    id: str
    direction: str
    title: str | None = None
    start_time: datetime
    end_time: datetime
    status: str
    is_mine: bool = False
    role: str | None = None  # 'mentor' | 'mentee' | None


class CreateSlotRequest(BaseModel):
    direction: str
    start_time: datetime
    end_time: datetime


class BookSlotRequest(BaseModel):
    start_time: datetime
    end_time: datetime


# ---- Session ----


class SessionOut(BaseModel):
    id: str
    slot_id: str
    direction: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str
    mentor_confirmed: bool
    mentee_confirmed: bool
    role: str | None = None  # joriy foydalanuvchi roli


class FinishSessionRequest(BaseModel):
    comment: str = Field(..., min_length=10)
    rating: int | None = Field(default=None, ge=1, le=5)


# ---- Leaderboard ----


class LeaderboardEntry(BaseModel):
    rank: int
    nickname: str
    xp: int
    level: int
    total_taught: int


class MessageResponse(BaseModel):
    detail: str


# ---- Constants ----


class DirectionOut(BaseModel):
    id: str
    name: str
    emoji: str
