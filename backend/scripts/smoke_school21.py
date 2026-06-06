"""Qo'lda smoke-test: School21Client haqiqiy API bilan ishlashini tekshiradi.

Ishlatish:
    S21_LOGIN=... S21_PASSWORD=... python -m scripts.smoke_school21

Bu test CI'da ishlamaydi (haqiqiy tarmoq kerak). Faqat qo'lda tekshirish uchun.
"""
from __future__ import annotations

import asyncio
import os

from bot.services.school21_api import School21Client


async def main() -> None:
    login = os.environ.get("S21_LOGIN")
    password = os.environ.get("S21_PASSWORD")
    if not login or not password:
        print("S21_LOGIN va S21_PASSWORD env o'zgaruvchilarini bering.")
        return

    client = School21Client()
    token = await client.authenticate(login, password)
    print("auth:", "OK" if token else "FAILED")
    if token:
        profile = await client.get_profile(login, token["access_token"])
        print("profile keys:", list(profile.keys()) if profile else None)
        directions = await client.suggest_directions(login, token["access_token"])
        print("suggested directions:", directions)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
