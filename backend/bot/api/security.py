"""Telegram Mini App initData validatsiyasi va JWT yordamchilari.

Telegram WebApp `initData` ni tekshirish (HMAC-SHA256) va JWT token
yaratish/tekshirish. Hujjat: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from jose import JWTError, jwt

from ..config import settings

_ALGORITHM = "HS256"


def validate_init_data(init_data: str, max_age_seconds: int = 86400) -> dict | None:
    """Telegram WebApp initData ni tekshiradi.

    Muvaffaqiyatda parse qilingan ma'lumotlarni (user dict bilan) qaytaradi,
    aks holda None.
    """
    if not init_data:
        return None

    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    # data_check_string: kalitlar alfavit tartibida, "key=value\n" bilan
    data_check_string = "\n".join(f"{k}={parsed[k]}" for k in sorted(parsed.keys()))

    # secret_key = HMAC_SHA256("WebAppData", bot_token)
    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    # auth_date eskirganligini tekshirish
    auth_date = parsed.get("auth_date")
    if auth_date is not None:
        try:
            if time.time() - int(auth_date) > max_age_seconds:
                return None
        except ValueError:
            return None

    # user maydoni JSON satr — parse qilamiz
    if "user" in parsed:
        try:
            parsed["user"] = json.loads(parsed["user"])
        except (ValueError, TypeError):
            return None

    return parsed


def create_access_token(user_id: int, extra: dict | None = None) -> str:
    """Foydalanuvchi uchun JWT access token yaratadi."""
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.JWT_EXPIRE_HOURS * 3600,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """JWT tokenni tekshirib, payload qaytaradi (yoki None)."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[_ALGORITHM])
    except JWTError:
        return None
