"""Auth endpoints: Telegram login, School21 login, refresh, logout, me.

School21 /participants/{login} haqiqiy field nomlari (tekshirilgan 2026-06):
  login, className, parallelName, expValue, level, expToNextLevel,
  campus: {id, shortName}, status
  — email, firstName, lastName bu API da YO'Q.
"""
from __future__ import annotations

import json
import logging

import httpx
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    encrypt_token,
    verify_telegram_init_data,
)
from app.db.models.user import User
from app.schemas.auth import (
    RefreshRequest,
    School21LoginRequest,
    TelegramLoginRequest,
    TokenResponse,
)
from app.schemas.user import UserMe
from app.services.school21_client import detect_main_track, school21_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _verify_init_data(init_data: str) -> dict:
    fields = verify_telegram_init_data(init_data)
    if fields is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )
    return fields


def _parse_tg_user(fields: dict) -> dict:
    raw = fields.get("user")
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram user payload missing",
        )
    return json.loads(raw)


def _issue_tokens(user: User) -> TokenResponse:
    subject = str(user.id)
    return TokenResponse(
        access_token=create_access_token(subject, {"admin": user.is_admin}),
        refresh_token=create_refresh_token(subject),
        onboarding_done=user.onboarding_done,
    )


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.post("/telegram", response_model=TokenResponse)
async def telegram_login(payload: TelegramLoginRequest, db: DbSession):
    """Mavjud foydalanuvchi uchun Telegram initData orqali login."""
    fields = _verify_init_data(payload.init_data)
    tg_user = _parse_tg_user(fields)
    telegram_id = int(tg_user["id"])

    user = (
        await db.execute(select(User).where(User.telegram_id == telegram_id))
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi. Avval School21 orqali ro'yxatdan o'ting.",
        )
    return _issue_tokens(user)


@router.post("/school21/login", response_model=TokenResponse)
async def school21_login(payload: School21LoginRequest, db: DbSession):
    """School21 orqali autentifikatsiya (birinchi kirishda user yaratadi)."""
    fields = _verify_init_data(payload.init_data)
    tg_user = _parse_tg_user(fields)
    telegram_id = int(tg_user["id"])
    telegram_username = tg_user.get("username")

    # 1. School21 Keycloak login
    try:
        token_data = await school21_client.login(payload.login, payload.password)
    except httpx.HTTPStatusError as exc:
        logger.warning("S21 auth error %s: %s", exc.response.status_code, exc.response.text[:200])
        if exc.response.status_code in (400, 401):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="School21 login yoki parol noto'g'ri",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"School21 API xatosi: {exc.response.status_code}",
        )
    except Exception as exc:
        logger.error("S21 connect error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="School21 API ga ulanib bo'lmadi",
        )

    s21_token = token_data.get("access_token") or token_data.get("accessToken")
    if not s21_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="School21 token missing in response",
        )

    # 2. Profil ma'lumotlari — faqat mavjud fieldlar
    profile = await school21_client.get_profile(s21_token, payload.login)

    # 3. Tugallangan loyihalar → main_track aniqlash
    try:
        finished = await school21_client.get_projects(
            s21_token, "FINISHED", login=payload.login
        )
    except Exception:
        finished = []
    main_track = detect_main_track(finished)

    # 4. Coalition nomi + location
    coalition_name: str | None = None
    current_location: str | None = None
    try:
        coalition = await school21_client.get_coalition(s21_token, payload.login)
        coalition_name = coalition.get("name")
    except Exception:
        pass
    try:
        workstation = await school21_client.get_location(s21_token, payload.login)
        current_location = workstation.get("formatted")
    except Exception:
        pass

    # 5. User yaratish yoki yangilash
    user = (
        await db.execute(select(User).where(User.school21_login == payload.login))
    ).scalar_one_or_none()

    if user is None:
        user = User(
            school21_login=payload.login,
            peer_points=5,
        )
        db.add(user)

    # Telegram ma'lumotlari
    user.telegram_id = telegram_id
    user.telegram_username = telegram_username
    user.school21_token_enc = encrypt_token(s21_token)

    # Ism: Telegram dan keladi (School21 API da yo'q)
    if not user.first_name:
        user.first_name = tg_user.get("first_name") or payload.login
    if not user.last_name and tg_user.get("last_name"):
        user.last_name = tg_user["last_name"]

    # Campus: {"id":..., "shortName":"21 Samarkand"}
    campus_raw = profile.get("campus")
    if isinstance(campus_raw, dict):
        user.campus = campus_raw.get("shortName") or user.campus
    elif isinstance(campus_raw, str) and campus_raw:
        user.campus = campus_raw

    # core_program: "className" → "25_08_SKD"
    if profile.get("className"):
        user.core_program = profile["className"]

    # Coalition
    if coalition_name:
        user.coalition_name = coalition_name

    # Current location (workstation)
    if current_location:
        user.current_location = current_location

    # main_track (loyihalar prefiks analizi)
    if main_track:
        user.main_track = main_track

    await db.commit()
    await db.refresh(user)
    return _issue_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: DbSession):
    import uuid
    data = decode_token(payload.refresh_token)
    if data is None or data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user = await db.get(User, uuid.UUID(data["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return _issue_tokens(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user: CurrentUser):
    """Stateless JWT — client tokenni o'chiradi."""
    return None


@router.get("/me", response_model=UserMe)
async def me(user: CurrentUser):
    return user
