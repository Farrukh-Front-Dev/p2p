"""Check /participants/{login}/workstation endpoint response structure."""
import asyncio, json
import httpx
from app.db.base import AsyncSessionLocal
from app.db.models.user import User
from app.core.security import decrypt_token
from app.services.school21_client import _BROWSER_UA
from sqlalchemy import select

BASE = "https://platform.21-school.ru/services/21-school/api/v1"


async def main():
    async with AsyncSessionLocal() as db:
        user = (
            await db.execute(select(User).where(User.school21_login == "toyneden"))
        ).scalar_one_or_none()
        if not user or not user.school21_token_enc:
            print("User topilmadi — avval login qiling")
            return
        token = decrypt_token(user.school21_token_enc)

    async with httpx.AsyncClient(
        headers={"User-Agent": _BROWSER_UA}, timeout=10
    ) as c:
        r = await c.get(
            f"{BASE}/participants/toyneden/workstation",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
