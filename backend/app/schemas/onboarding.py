"""Onboarding schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TrackResponse(BaseModel):
    core_program: str | None = None
    main_track: str | None = None


class ConfirmTrackRequest(BaseModel):
    main_track: str


class LanguagesRequest(BaseModel):
    languages: list[str] = Field(min_length=1)


class OnboardingStatus(BaseModel):
    onboarding_done: bool
    main_track: str | None = None
    languages: list[str]
