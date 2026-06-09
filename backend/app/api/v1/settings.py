"""User settings endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/settings", tags=["settings"])


class LanguageUpdate(BaseModel):
    language: str


class ThemeUpdate(BaseModel):
    theme: str  # 'light' | 'dark'


@router.get("/")
async def get_settings(user: CurrentUser):
    return {
        "languages": user.languages,
        "campus": user.campus,
    }


@router.patch("/language")
async def update_language(payload: LanguageUpdate, user: CurrentUser, db: DbSession):
    langs = list(user.languages or [])
    if payload.language not in langs:
        langs.insert(0, payload.language)
    user.languages = langs
    await db.commit()
    return {"languages": user.languages}


@router.patch("/theme")
async def update_theme(payload: ThemeUpdate, user: CurrentUser):
    # Theme is a client-side preference; echoed back for confirmation.
    return {"theme": payload.theme}
