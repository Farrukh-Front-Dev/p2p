"""Admin main menu and entry point."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.core.config import settings
from bot.constants import ADM_MENU
from bot.keyboards import admin_main_kb


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin huquqi yo'q.")
        return ConversationHandler.END
    await update.message.reply_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
    return ADM_MENU


async def main_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "am_close":
        await q.message.delete()
        return ConversationHandler.END
    if d == "am_back":
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU
    if d == "am_ch":
        from bot.handlers.admin.channels import channels_list_cb
        return await channels_list_cb(q, context)
    if d == "am_usr":
        from bot.handlers.admin.users import show_users_menu
        return await show_users_menu(q)
    if d == "am_stat":
        from bot.handlers.admin.stats import show_stats
        return await show_stats(q)
    if d == "am_bcast":
        from bot.handlers.admin.broadcast import show_broadcast_menu
        return await show_broadcast_menu(q)
    if d == "am_set":
        from bot.handlers.admin.settings import show_settings
        return await show_settings(q)
    return ADM_MENU


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Admin panel yopildi.")
    return ConversationHandler.END
