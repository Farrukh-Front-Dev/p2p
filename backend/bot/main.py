"""Bot ishga tushirish (polling / webhook)."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from .config import settings
from .handlers import (
    admin,
    auth,
    chat,
    finish,
    learn,
    menu,
    profile,
    slots,
    teach,
)
from .handlers import settings as settings_h
from .middlewares.auth_middleware import AuthMiddleware
from .middlewares.i18n_middleware import I18nMiddleware
from .middlewares.throttling import ThrottlingMiddleware
from .services.scheduler_service import SchedulerService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    # Middlewares (tartib muhim: throttling -> auth -> i18n)
    for observer in (dp.message, dp.callback_query):
        observer.middleware(ThrottlingMiddleware())
        observer.middleware(AuthMiddleware())
        observer.middleware(I18nMiddleware())

    # Routerlar (chat relay OXIRIDA — catch-all)
    dp.include_router(auth.router)
    dp.include_router(admin.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(slots.router)
    dp.include_router(teach.router)
    dp.include_router(learn.router)
    dp.include_router(finish.router)
    dp.include_router(settings_h.router)
    dp.include_router(chat.router)
    return dp


def create_bot() -> Bot:
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def run_polling() -> None:
    bot = create_bot()
    dp = create_dispatcher()

    scheduler = SchedulerService(bot)
    scheduler.start()

    logger.info("Bot polling rejimida ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


def main() -> None:
    if settings.DEBUG:
        asyncio.run(run_polling())
    else:
        from .webhook_server import run_webhook

        run_webhook()


if __name__ == "__main__":
    main()
