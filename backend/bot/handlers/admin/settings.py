"""🔧 Sozlamalar bo'limi — subscription toggle, maintenance, webapp URL."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.constants import ADM_MENU, ADM_SETTINGS_WEBAPP
from bot.keyboards import admin_main_kb
from bot.services.settings_service import get_settings, update_settings


async def show_settings(q) -> int:
    s = await get_settings()
    sub = "🟢" if s.subscription_enabled else "🔴"
    maint = "🔴 ON" if s.maintenance_mode else "🟢 OFF"
    url = s.webapp_url or "(o'rnatilmagan)"
    text = (
        "🔧 <b>Sozlamalar</b>\n\n"
        f"📢 Obuna: {sub}\n"
        f"🔧 Maintenance: {maint}\n"
        f"🌐 WebApp: <code>{url}</code>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📢 Obuna o'chirish" if s.subscription_enabled else "📢 Obuna yoqish",
            callback_data="set_sub_toggle",
        )],
        [InlineKeyboardButton(
            "🔧 Maintenance o'chirish" if s.maintenance_mode else "🔧 Maintenance yoqish",
            callback_data="set_maint_toggle",
        )],
        [InlineKeyboardButton("🌐 WebApp URL", callback_data="set_webapp")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")],
    ])
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    return ADM_MENU


async def settings_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "set_sub_toggle":
        s = await get_settings()
        await update_settings(subscription_enabled=not s.subscription_enabled)
        return await show_settings(q)
    if d == "set_maint_toggle":
        s = await get_settings()
        await update_settings(maintenance_mode=not s.maintenance_mode)
        return await show_settings(q)
    if d == "set_webapp":
        await q.message.edit_text("🌐 Yangi WebApp URL (https://...):")
        return ADM_SETTINGS_WEBAPP
    return ADM_MENU


async def webapp_url_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()
    if not url.startswith("https://"):
        await update.message.reply_text("❌ https:// bilan boshlang:")
        return ADM_SETTINGS_WEBAPP
    await update_settings(webapp_url=url)
    await update.message.reply_text(f"✅ WebApp: <code>{url}</code>", parse_mode="HTML", reply_markup=admin_main_kb())
    return ADM_MENU
