"""Common commands: /help, /webapp."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.start import _webapp_keyboard, help_cmd, webapp_cmd

# Re-export — bot/main.py dan import qilinadi
__all__ = ["help_cmd", "webapp_cmd"]
