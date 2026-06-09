"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.cache import close_redis
from app.services.school21_client import school21_client
from app.ws.slot_ws import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create the shared httpx client (connection pool).
    await school21_client.start()
    yield
    # Shutdown: close clients.
    await school21_client.stop()
    await close_redis()


app = FastAPI(
    title="P2P Platform",
    version="3.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)

# Mount SQLAdmin panel.
try:
    from admin.setup import init_admin

    init_admin(app)
except Exception:  # pragma: no cover - admin is optional at boot
    pass


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
