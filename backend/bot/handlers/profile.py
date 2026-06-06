"""Profil ko'rsatish handleri."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..constants import direction_label
from ..keyboards.main_menu import get_main_menu_kb
from ..utils.level_utils import get_level_info

router = Router()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, user=None, lang: str = "uz"):
    if user is None:
        await callback.answer()
        return

    info = get_level_info(user.xp)
    directions = ", ".join(direction_label(d) for d in user.directions) or "—"

    text = (
        "👤 <b>Profil</b>\n\n"
        f"🆔 {('@' + user.username) if user.username else (user.nickname or user.school21_login)}\n"
        f"📊 Reyting: {user.rating:.0f}%\n"
        f"🏆 Daraja: {info['level']} — {info['name']} ({user.xp} XP)\n"
        f"🪙 Tangalar: {user.coins}/{user.max_coins}\n\n"
        "📈 <b>Statistika</b>\n"
        f"   O'rgatgan: {user.total_taught} sessiya\n"
        f"   O'rgangan: {user.total_learned} sessiya\n\n"
        "📚 <b>Yo'nalishlar</b>\n"
        f"   {directions}\n\n"
        f"🎯 Keyingi daraja: {info['progress']}% "
        f"({info['xp_needed']} XP kerak)"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_kb(lang))
    await callback.answer()
