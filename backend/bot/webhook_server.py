"""FastAPI webhook server (production rejimi) + Mini App REST API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .api.app import api_router
from .config import settings
from .main import create_bot, create_dispatcher
from .services.scheduler_service import SchedulerService

logger = logging.getLogger(__name__)

bot = None
dp = None
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, dp, scheduler
    bot = create_bot()
    dp = create_dispatcher()
    scheduler = SchedulerService(bot)
    scheduler.start()

    webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.SECRET_KEY,
        drop_pending_updates=True,
    )
    logger.info("Webhook o'rnatildi: %s", webhook_url)
    yield
    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(title="PeerLearn Mini App API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mini App REST API
app.include_router(api_router)


@app.post(settings.WEBHOOK_PATH)
async def telegram_webhook(request: Request) -> Response:
    # Webhook secret tekshiruvi
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.SECRET_KEY:
        return Response(status_code=401)

    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return Response(status_code=200)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def run_webhook() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)
