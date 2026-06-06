"""Mini App REST API router'larini bir joyga yig'ish."""

from __future__ import annotations

from fastapi import APIRouter

from . import routes_auth, routes_sessions, routes_slots, routes_users

api_router = APIRouter()
api_router.include_router(routes_auth.router)
api_router.include_router(routes_users.router)
api_router.include_router(routes_slots.router)
api_router.include_router(routes_sessions.router)
