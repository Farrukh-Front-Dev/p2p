"""Telegram bot entry point (webhook mode in production, polling for dev)."""
from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler

from app.core.config import settings
from bot.handlers import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("webapp", commands.webapp))
    app.add_handler(CommandHandler("profile", commands.profile))
    app.add_handler(CommandHandler("slots", commands.slots))
    app.add_handler(CommandHandler("help", commands.help_command))
    app.add_handler(CommandHandler("cancel", commands.cancel))
    return app


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    app = build_application()
    logger.info("Starting bot in polling mode")
    app.run_polling()


if __name__ == "__main__":
    main()
