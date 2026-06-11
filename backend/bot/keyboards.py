"""Reusable keyboards for the bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanallar", callback_data="am_ch"),
         InlineKeyboardButton("👤 Foydalanuvchilar", callback_data="am_usr")],
        [InlineKeyboardButton("📊 Statistika", callback_data="am_stat"),
         InlineKeyboardButton("📣 Broadcast", callback_data="am_bcast")],
        [InlineKeyboardButton("🔧 Sozlamalar", callback_data="am_set")],
        [InlineKeyboardButton("❌ Yopish", callback_data="am_close")],
    ])


def back_kb(callback_data: str = "am_back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Orqaga", callback_data=callback_data)]
    ])
