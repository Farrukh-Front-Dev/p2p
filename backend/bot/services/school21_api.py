"""School 21 API klienti (Keycloak password grant + REST profil).

Haqiqiy oqim (tasdiqlangan):
- Token: POST {S21_TOKEN_URL} (client_id=s21-open-api, grant_type=password)
- Profil: GET {S21_API_URL}/participants/{login}  (Bearer token)
- Skills: GET {S21_API_URL}/participants/{login}/skills
"""

from __future__ import annotations

import logging

import httpx

from ..config import settings
from ..constants import suggest_directions_from_skills

logger = logging.getLogger(__name__)


class School21Client:
    def __init__(self, timeout: float = 30.0):
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def authenticate(self, login: str, password: str) -> dict | None:
        """Keycloak password grant orqali token oladi.

        Muvaffaqiyatda {access_token, refresh_token, expires_in, ...},
        aks holda None qaytaradi.
        """
        try:
            response = await self.client.post(
                settings.S21_TOKEN_URL,
                data={
                    "client_id": settings.S21_CLIENT_ID,
                    "grant_type": "password",
                    "username": login,
                    "password": password,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.HTTPError as exc:
            logger.warning("School21 auth network error: %s", exc)
            return None

        if response.status_code != 200:
            logger.info("School21 auth failed: status=%s", response.status_code)
            return None

        try:
            data = response.json()
        except ValueError:
            logger.warning("School21 auth: invalid JSON response")
            return None

        if "access_token" not in data:
            return None
        return data

    async def get_profile(self, login: str, access_token: str) -> dict | None:
        """Foydalanuvchi profilini oladi.

        Qaytaradi: {login, className, parallelName, expValue, level,
                    expToNextLevel, campus, status} yoki None.
        """
        try:
            response = await self.client.get(
                f"{settings.S21_API_URL}/participants/{login}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.HTTPError as exc:
            logger.warning("School21 profile network error: %s", exc)
            return None

        if response.status_code != 200:
            logger.info("School21 profile failed: status=%s", response.status_code)
            return None

        try:
            return response.json()
        except ValueError:
            return None

    async def get_skills(self, login: str, access_token: str) -> list[dict]:
        """Foydalanuvchi skill'larini oladi: [{name, points}, ...]."""
        try:
            response = await self.client.get(
                f"{settings.S21_API_URL}/participants/{login}/skills",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.HTTPError as exc:
            logger.warning("School21 skills network error: %s", exc)
            return []

        if response.status_code != 200:
            return []

        try:
            data = response.json()
        except ValueError:
            return []

        skills = data.get("skills", data) if isinstance(data, dict) else data
        return skills if isinstance(skills, list) else []

    async def suggest_directions(self, login: str, access_token: str) -> list[str]:
        """Skill'lar asosida yo'nalishlarni taklif qiladi."""
        skills = await self.get_skills(login, access_token)
        return suggest_directions_from_skills(skills)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


# Global instansiya (handlerlarda ishlatish uchun)
school21_api = School21Client()
