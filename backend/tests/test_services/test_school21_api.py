"""School21Client testlari (respx bilan httpx mock)."""

from __future__ import annotations

import httpx
import pytest
import respx

from bot.config import settings
from bot.services.school21_api import School21Client


@pytest.mark.asyncio
@respx.mock
async def test_authenticate_success():
    respx.post(settings.S21_TOKEN_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "tok123",
                "refresh_token": "ref123",
                "expires_in": 36000,
                "token_type": "Bearer",
            },
        )
    )
    client = School21Client()
    result = await client.authenticate("toyneden", "secret")
    await client.close()

    assert result is not None
    assert result["access_token"] == "tok123"
    assert result["expires_in"] == 36000


@pytest.mark.asyncio
@respx.mock
async def test_authenticate_invalid_credentials():
    respx.post(settings.S21_TOKEN_URL).mock(
        return_value=httpx.Response(401, json={"error": "invalid_grant"})
    )
    client = School21Client()
    result = await client.authenticate("toyneden", "wrong")
    await client.close()

    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_authenticate_network_error():
    respx.post(settings.S21_TOKEN_URL).mock(side_effect=httpx.ConnectError("boom"))
    client = School21Client()
    result = await client.authenticate("x", "y")
    await client.close()
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_parses_fields():
    login = "toyneden"
    respx.get(f"{settings.S21_API_URL}/participants/{login}").mock(
        return_value=httpx.Response(
            200,
            json={
                "login": "toyneden",
                "className": "25_08_SKD",
                "parallelName": "Core program",
                "expValue": 12401,
                "level": 10,
                "expToNextLevel": 1098,
                "campus": {"id": "abc", "shortName": "21 Samarkand"},
                "status": "ACTIVE",
            },
        )
    )
    client = School21Client()
    profile = await client.get_profile(login, "tok")
    await client.close()

    assert profile["login"] == "toyneden"
    assert profile["level"] == 10
    assert profile["expValue"] == 12401
    assert profile["campus"]["shortName"] == "21 Samarkand"


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_unauthorized():
    login = "toyneden"
    respx.get(f"{settings.S21_API_URL}/participants/{login}").mock(return_value=httpx.Response(401))
    client = School21Client()
    profile = await client.get_profile(login, "badtok")
    await client.close()
    assert profile is None


@pytest.mark.asyncio
@respx.mock
async def test_suggest_directions_from_skills():
    login = "toyneden"
    respx.get(f"{settings.S21_API_URL}/participants/{login}/skills").mock(
        return_value=httpx.Response(
            200,
            json={
                "skills": [
                    {"name": "ML & AI", "points": 3651},
                    {"name": "Algorithms", "points": 1778},
                    {"name": "Python", "points": 1704},
                    {"name": "C", "points": 993},
                    {"name": "SQL", "points": 58},
                ]
            },
        )
    )
    client = School21Client()
    directions = await client.suggest_directions(login, "tok")
    await client.close()

    # Eng yuqori ball ML & AI -> ml_ai birinchi
    assert directions[0] == "ml_ai"
    assert "python" in directions
    assert "algorithms" in directions
    assert len(directions) <= 5


@pytest.mark.asyncio
@respx.mock
async def test_get_skills_empty_on_error():
    login = "toyneden"
    respx.get(f"{settings.S21_API_URL}/participants/{login}/skills").mock(
        return_value=httpx.Response(500)
    )
    client = School21Client()
    skills = await client.get_skills(login, "tok")
    await client.close()
    assert skills == []
