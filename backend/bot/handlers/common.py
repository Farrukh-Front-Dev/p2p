"""Common commands: /help, /webapp."""
from __future__ import annotations


from bot.handlers.start import help_cmd, webapp_cmd

# Re-export — bot/main.py dan import qilinadi
__all__ = ["help_cmd", "webapp_cmd"]
