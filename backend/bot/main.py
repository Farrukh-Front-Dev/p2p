"""Telegram bot entry point."""
from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler

from app.core.config import settings
from bot.handlers.start import get_start_handler, help_cmd, webapp_cmd
from bot.handlers.admin import get_admin_handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)


def build_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(get_start_handler())
    app.add_handler(get_admin_handler())
    app.add_handler(CommandHandler("webapp", webapp_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    return app


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    app = build_application()
    logger.info("Starting bot in polling mode")
    app.run_polling()


if __name__ == "__main__":
    main()
