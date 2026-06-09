"""Onboarding endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.onboarding import (
    ConfirmTrackRequest,
    LanguagesRequest,
    OnboardingStatus,
    TrackResponse,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/track", response_model=TrackResponse)
async def get_track(user: CurrentUser):
    return TrackResponse(core_program=user.core_program, main_track=user.main_track)


@router.post("/confirm", response_model=TrackResponse)
async def confirm_track(payload: ConfirmTrackRequest, user: CurrentUser, db: DbSession):
    user.main_track = payload.main_track
    await db.commit()
    return TrackResponse(core_program=user.core_program, main_track=user.main_track)


@router.post("/languages", response_model=OnboardingStatus)
async def set_languages(payload: LanguagesRequest, user: CurrentUser, db: DbSession):
    user.languages = payload.languages
    user.onboarding_done = True
    await db.commit()
    return OnboardingStatus(
        onboarding_done=user.onboarding_done,
        main_track=user.main_track,
        languages=user.languages,
    )


@router.get("/status", response_model=OnboardingStatus)
async def status(user: CurrentUser):
    return OnboardingStatus(
        onboarding_done=user.onboarding_done,
        main_track=user.main_track,
        languages=user.languages,
    )
