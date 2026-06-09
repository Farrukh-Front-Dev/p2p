#!/usr/bin/env python3
"""Generate a valid signed Telegram WebApp initData for local testing.

Bu script hech qanday loyiha importiga bog'liq emas — to'g'ridan-to'g'ri
python3 bilan yoki .venv orqali ishlaydi.

Ishlatish:
    # peer_learn papkasidan:
    python3 scripts/gen_init_data.py
    python3 scripts/gen_init_data.py --id 12345 --username alice --first Alice

    # Yoki .venv bilan:
    .venv/bin/python3 scripts/gen_init_data.py

    # Bot token argument sifatida berish:
    python3 scripts/gen_init_data.py --token 123456:ABC...
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode


def build_init_data(
    user_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None = None,
    bot_token: str | None = None,
) -> str:
    # Token: argument > env > xato
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise SystemExit(
            "Bot token topilmadi.\n"
            "  --token argument bering yoki .env da TELEGRAM_BOT_TOKEN o'rnating."
        )

    user_obj: dict = {"id": user_id, "first_name": first_name}
    if last_name:
        user_obj["last_name"] = last_name
    if username:
        user_obj["username"] = username

    fields = {
        "auth_date": str(int(time.time())),
        "query_id": "AAEtest_query_id",
        "user": json.dumps(user_obj, separators=(",", ":")),
    }

    # Telegram spetsifikatsiyasiga ko'ra: maydonlar saralanib \n bilan qo'shiladi
    data_check_string = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))

    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    return urlencode(fields)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Telegram WebApp initData generator (test uchun)"
    )
    parser.add_argument("--id",       type=int,   default=999000111,  help="Telegram user ID")
    parser.add_argument("--username", type=str,   default="test_user", help="@username")
    parser.add_argument("--first",    type=str,   default="Test",      help="first_name")
    parser.add_argument("--last",     type=str,   default=None,        help="last_name")
    parser.add_argument("--token",    type=str,   default=None,        help="Bot token (agar .env da yo'q bo'lsa)")
    args = parser.parse_args()

    # .env faylini qo'lda o'qiymiz (python-dotenv talab qilmasin deb)
    _load_dotenv()

    init_data = build_init_data(
        user_id=args.id,
        username=args.username,
        first_name=args.first,
        last_name=args.last,
        bot_token=args.token,
    )

    print("\n" + "="*60)
    print("✅  Test initData (Swagger yoki curl uchun):")
    print("="*60)
    print(init_data)
    print("="*60)
    print(f"\nTelegram user_id : {args.id}")
    print(f"username         : {args.username}")
    print(f"first_name       : {args.first}")
    print("\nJSON (POST body uchun):")
    print(json.dumps({"init_data": init_data}, indent=2))


def _load_dotenv() -> None:
    """Minimal .env loader — python-dotenv o'rnatilmasa ham ishlaydi."""
    for candidate in [".env", "../.env"]:
        if os.path.isfile(candidate):
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        os.environ.setdefault(key.strip(), val.strip())
            break


if __name__ == "__main__":
    main()
