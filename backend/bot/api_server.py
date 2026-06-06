"""Mustaqil REST API server (Mini App frontend uchun).

Bot polling rejimida ishlayotganda ham API'ni alohida ishga tushirish uchun:
    python -m bot.api_server

Production'da webhook_server.py allaqachon API'ni o'z ichiga oladi.
"""

from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.app import api_router
from .config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="PeerLearn Mini App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
