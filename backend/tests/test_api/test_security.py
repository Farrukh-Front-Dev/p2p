"""initData validatsiyasi va JWT testlari."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

from bot.api.security import (
    create_access_token,
    decode_access_token,
    validate_init_data,
)
from bot.config import settings


def _make_init_data(user: dict, bot_token: str, auth_date: int | None = None) -> str:
    auth_date = auth_date or int(time.time())
    fields = {
        "user": json.dumps(user, separators=(",", ":")),
        "auth_date": str(auth_date),
        "query_id": "AAH123",
    }
    data_check_string = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    fields["hash"] = h
    return urlencode(fields)


def test_validate_init_data_valid():
    user = {"id": 123, "first_name": "Toyne", "username": "toyne"}
    init = _make_init_data(user, settings.BOT_TOKEN)
    result = validate_init_data(init)
    assert result is not None
    assert result["user"]["id"] == 123
    assert result["user"]["username"] == "toyne"


def test_validate_init_data_tampered():
    user = {"id": 123}
    init = _make_init_data(user, settings.BOT_TOKEN)
    # hash'ni buzamiz
    tampered = init.replace("hash=", "hash=deadbeef")
    assert validate_init_data(tampered) is None


def test_validate_init_data_wrong_token():
    user = {"id": 123}
    init = _make_init_data(user, "999:WRONGTOKEN")
    assert validate_init_data(init) is None


def test_validate_init_data_expired():
    user = {"id": 123}
    old = int(time.time()) - 100000
    init = _make_init_data(user, settings.BOT_TOKEN, auth_date=old)
    assert validate_init_data(init, max_age_seconds=3600) is None


def test_jwt_roundtrip():
    token = create_access_token(456)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "456"


def test_jwt_invalid():
    assert decode_access_token("not.a.token") is None
