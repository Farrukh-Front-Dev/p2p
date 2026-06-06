"""Autentifikatsiya endpointlari (Telegram Mini App)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..repositories.user_repo import UserRepository
from ..services.school21_api import school21_api
from .deps import get_db_session
from .schemas import AuthRequest, AuthResponse, RegisterRequest, UserOut
from .security import (
    create_access_token,
    decode_access_token,
    validate_init_data,
)
from .serializers import user_to_out

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Bearer token kerak")
    return authorization.split(" ", 1)[1].strip()


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(
    body: AuthRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Telegram WebApp initData orqali kirish.

    Agar foydalanuvchi ro'yxatdan o'tgan bo'lsa — token + profil qaytaradi.
    Aks holda is_new_user=True bo'ladi (frontend ro'yxatdan o'tishga yo'naltiradi).
    """
    data = validate_init_data(body.init_data)
    if data is None or "user" not in data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="initData yaroqsiz",
        )

    tg_user = data["user"]
    user_id = tg_user.get("id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="user.id topilmadi")

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    token = create_access_token(user_id)
    if user is None or not user.is_active:
        # Hali ro'yxatdan o'tmagan — vaqtinchalik token bilan ro'yxatga yo'naltiramiz
        return AuthResponse(
            access_token=token,
            is_new_user=True,
            user=UserOut(
                id=user_id,
                username=tg_user.get("username"),
                nickname=tg_user.get("first_name"),
                school21_login=None,
                language=tg_user.get("language_code", "uz"),
                directions=[],
                coins=0,
                max_coins=0,
                xp=0,
                level=1,
                level_name="Newbie 🌱",
                level_progress=0,
                xp_to_next=100,
                rating=0.0,
                total_taught=0,
                total_learned=0,
            ),
        )

    return AuthResponse(access_token=token, is_new_user=False, user=user_to_out(user))


@router.post("/register", response_model=AuthResponse)
async def register(
    body: RegisterRequest,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db_session),
):
    """Ro'yxatdan o'tishni yakunlash.

    /telegram dan olingan token (Authorization: Bearer ...) orqali user_id
    aniqlanadi. School 21 login/parol tekshiriladi, foydalanuvchi yaratiladi.
    """
    token = _bearer(authorization)
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Token yaroqsiz")
    user_id = int(payload["sub"])

    if not body.directions:
        raise HTTPException(status_code=400, detail="Kamida 1 ta yo'nalish tanlang")

    # School 21 tekshiruvi
    token_data = await school21_api.authenticate(body.school21_login, body.school21_password)
    if not token_data:
        raise HTTPException(status_code=401, detail="School 21 login yoki parol noto'g'ri")

    profile = await school21_api.get_profile(body.school21_login, token_data["access_token"]) or {}

    repo = UserRepository(db)
    user = await repo.create_or_update(
        user_id=user_id,
        username=None,
        school21_login=profile.get("login", body.school21_login),
        nickname=profile.get("login", body.school21_login),
        avatar_url=None,
        directions=body.directions[:5],
        language=body.language,
        level=1,
        xp=0,
    )
    await db.flush()

    new_token = create_access_token(user_id)
    return AuthResponse(access_token=new_token, is_new_user=False, user=user_to_out(user))


@router.post("/dev", response_model=AuthResponse)
async def auth_dev(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """FAQAT DEVELOPMENT (DEBUG=True): initData'siz token olish.

    Telegram Mini App'siz API'ni sinash uchun. Berilgan user_id uchun JWT
    qaytaradi. Agar foydalanuvchi mavjud bo'lsa profili bilan, aks holda
    is_new_user=True bilan.

    Production'da (DEBUG=False) bu endpoint 404 qaytaradi.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    token = create_access_token(user_id)

    if user is None or not user.is_active:
        return AuthResponse(
            access_token=token,
            is_new_user=True,
            user=UserOut(
                id=user_id,
                username=None,
                nickname=f"dev{user_id}",
                school21_login=None,
                language="uz",
                directions=[],
                coins=0,
                max_coins=0,
                xp=0,
                level=1,
                level_name="Newbie 🌱",
                level_progress=0,
                xp_to_next=100,
                rating=0.0,
                total_taught=0,
                total_learned=0,
            ),
        )

    return AuthResponse(access_token=token, is_new_user=False, user=user_to_out(user))
