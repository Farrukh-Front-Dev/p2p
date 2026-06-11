"""📊 Statistika bo'limi."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.constants import ADM_MENU
from bot.services.channel_service import get_all_channels
from bot.services.user_service import get_platform_stats


async def show_stats(q) -> int:
    s = await get_platform_stats()
    channels = await get_all_channels()
    active_ch = sum(1 for c in channels if c.is_active)
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {s['users']}\n"
        f"🟢 Faol: {s['active']} | 🔑 Tizimda: {s['logged_in']}\n"
        f"👑 Adminlar: {s['admins']}\n\n"
        f"📅 Slotlar: {s['slots']}\n"
        f"📖 Ochiq: {s['open']} | 📌 Band: {s['booked']} | ✅ Tugallangan: {s['completed']}\n"
        f"⏱ O'rtacha: {s['avg_minutes']} daq\n\n"
        f"📢 Kanallar: {len(channels)} (faol: {active_ch})"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Yangilash", callback_data="am_stat")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")],
    ])
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    return ADM_MENU
