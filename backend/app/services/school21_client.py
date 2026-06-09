"""Async httpx client for the School21 API.

Tasdiqlangan haqiqiy endpointlar (p2p loyihasidan):
  Auth:    POST https://auth.21-school.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token
  Profile: GET  {API_BASE}/participants/{login}
  Skills:  GET  {API_BASE}/participants/{login}/skills
  Projects:GET  {API_BASE}/participants/{login}/projects?status=...  (taxminiy)

XP, Level, Peer Points, Peer Coins — School21 dan OLINMAYDI.
"""
from __future__ import annotations

import logging
from collections import Counter
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

KEYCLOAK_TOKEN_URL = (
    "https://auth.21-school.ru/auth/realms/EduPowerKeycloak"
    "/protocol/openid-connect/token"
)
KEYCLOAK_CLIENT_ID = "s21-open-api"

# WAF oldidagi proxy bot user-agent larni bloklaydi.
_BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class School21Client:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or settings.SCHOOL21_API_BASE
        self._api_client: httpx.AsyncClient | None = None
        self._auth_client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        headers = {"User-Agent": _BROWSER_UA}
        if self._api_client is None:
            self._api_client = httpx.AsyncClient(
                base_url=self._base_url, headers=headers, timeout=15.0
            )
        if self._auth_client is None:
            self._auth_client = httpx.AsyncClient(headers=headers, timeout=15.0)

    async def stop(self) -> None:
        for c in (self._api_client, self._auth_client):
            if c is not None:
                await c.aclose()
        self._api_client = None
        self._auth_client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._api_client is None:
            raise RuntimeError("School21Client not started")
        return self._api_client

    @property
    def auth_client(self) -> httpx.AsyncClient:
        if self._auth_client is None:
            raise RuntimeError("School21Client not started")
        return self._auth_client

    # ── Authentication ────────────────────────────────────────────────────────

    async def login(self, login: str, password: str) -> dict[str, Any]:
        """Keycloak password grant — access_token, refresh_token qaytaradi."""
        resp = await self.auth_client.post(
            KEYCLOAK_TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "grant_type": "password",
                "username": login,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

    async def refresh_school21_token(self, refresh_token: str) -> dict[str, Any]:
        resp = await self.auth_client.post(
            KEYCLOAK_TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

    # ── Profile ───────────────────────────────────────────────────────────────

    async def get_profile(self, token: str, login: str) -> dict[str, Any]:
        """GET /participants/{login} — asosiy profil ma'lumotlari."""
        resp = await self.client.get(
            f"/participants/{login}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_location(self, token: str, login: str) -> dict[str, Any]:
        """GET /participants/{login}/workstation
        
        Returns: {clusterId, clusterName, row, number}
        Formatted as: "tillakori j5"
        """
        try:
            resp = await self.client.get(
                f"/participants/{login}/workstation",
                headers={"Authorization": f"Bearer {token}"},
            )
            if resp.status_code in (404, 204):
                return {}
            resp.raise_for_status()
            data = resp.json()
            # Format: "tillakori j5"
            cluster = data.get("clusterName", "")
            row = data.get("row", "")
            number = data.get("number", "")
            if cluster:
                data["formatted"] = f"{cluster} {row}{number}".strip()
            return data
        except httpx.HTTPStatusError:
            return {}
        except Exception:
            return {}

    # ── Projects ──────────────────────────────────────────────────────────────

    async def get_projects(
        self,
        token: str,
        status_filter: str,
        login: str | None = None,
    ) -> list[dict[str, Any]]:
        """GET /participants/{login}/projects?statusList=FINISHED|IN_PROGRESS"""
        if not login:
            raise ValueError("login required for get_projects")
        resp = await self.client.get(
            f"/participants/{login}/projects",
            params={"statusList": status_filter},
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code in (404, 400):
            return []
        resp.raise_for_status()
        data = resp.json()
        # Response: {"projects": [...]} yoki to'g'ridan-to'g'ri list
        return data.get("projects", []) if isinstance(data, dict) else data

    # ── Skills ────────────────────────────────────────────────────────────────

    async def get_skills(self, token: str, login: str) -> dict[str, Any]:
        """GET /participants/{login}/skills"""
        resp = await self.client.get(
            f"/participants/{login}/skills",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        return resp.json()

    async def get_coalition(self, token: str, login: str) -> dict[str, Any]:
        """GET /participants/{login}/coalition — agar mavjud bo'lsa."""
        try:
            resp = await self.client.get(
                f"/participants/{login}/coalition",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError:
            return {}


# ── main_track detection ──────────────────────────────────────────────────────

def detect_main_track(finished_projects: list[dict[str, Any]]) -> str | None:
    """Oxirgi 3 ta tugallangan loyiha prefiks bo'yicha asosiy yo'nalishni aniqlaydi.

    Projects endpoint: {"title": "C6_simple_shell", "completionDateTime": ..., "status": "FINISHED"}
    """
    if not finished_projects:
        return None

    # Faqat FINISHED statuslilarni olish
    finished = [p for p in finished_projects if p.get("status") == "FINISHED"]
    if not finished:
        # Agar filtr ishlasa barcha kelganlar FINISHED — hammasini ishlatamiz
        finished = finished_projects

    def sort_key(p: dict[str, Any]) -> str:
        return p.get("completionDateTime") or p.get("deadline") or ""

    recent = sorted(finished, key=sort_key, reverse=True)[:3]
    prefixes: list[str] = []
    for proj in recent:
        # Haqiqiy field: "title" (masalan "C6_simple_shell" yoki "APP1 Bootcamp. Day00")
        name = proj.get("title") or proj.get("name") or ""
        if "_" in name:
            prefixes.append(name.split("_", 1)[0])
        elif name:
            prefixes.append(name.split(".")[0].strip())

    if not prefixes:
        return None
    return Counter(prefixes).most_common(1)[0][0]


# Module-level singleton — app lifespan da start/stop qilinadi.
school21_client = School21Client()
