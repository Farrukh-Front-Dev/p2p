"""👤 Foydalanuvchilar bo'limi."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.constants import ADM_MENU, ADM_USERS_MENU, ADM_USERS_SEARCH, ADM_USER_DETAIL, ADM_USER_XP_INPUT, ADM_USER_POINTS_INPUT
from bot.keyboards import admin_main_kb
from bot.services.user_service import (
    get_user_stats_summary, get_recent_users, search_users,
    get_user_by_login, toggle_user_admin, toggle_user_block,
    adjust_user_xp, adjust_user_points, force_logout, unlink_telegram,
)


async def show_users_menu(q) -> int:
    stats = await get_user_stats_summary()
    recent = await get_recent_users(5)
    text = (
        "👤 <b>Foydalanuvchilar</b>\n\n"
        f"📊 Jami: {stats['total']} | Faol: {stats['active']} | Bloklangan: {stats['blocked']}\n"
        f"🆕 Bugun: {stats['new_today']} | 🔑 Tizimda: {stats['logged_in']}\n\n"
        "🕐 <b>Oxirgi:</b>\n"
    )
    for u in recent:
        text += f"  {'👑' if u.is_admin else '👤'} {u.school21_login} ({u.campus or '?'})\n"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Qidirish", callback_data="usr_search")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")],
    ])
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    return ADM_USERS_MENU


async def users_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    if q.data == "am_back":
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU
    if q.data == "usr_search":
        await q.message.edit_text("🔍 Login yoki username kiriting:")
        return ADM_USERS_SEARCH
    return ADM_USERS_MENU


async def users_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    users = await search_users(update.message.text.strip())
    if not users:
        await update.message.reply_text("❌ Topilmadi.", reply_markup=admin_main_kb())
        return ADM_MENU
    buttons = [
        [InlineKeyboardButton(f"{'👑' if u.is_admin else '👤'} {u.school21_login}", callback_data=f"usr_{u.school21_login}")]
        for u in users
    ]
    buttons.append([InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")])
    await update.message.reply_text(f"🔍 {len(users)} ta:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    return ADM_USER_DETAIL


async def user_detail_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "am_back":
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU
    if d == "usr_search":
        await q.message.edit_text("🔍 Login yoki username kiriting:")
        return ADM_USERS_SEARCH
    if d.startswith("usr_admin_"):
        login = d[len("usr_admin_"):]
        await toggle_user_admin(login)
        await q.answer("O'zgartirildi", show_alert=True)
        return await _detail(q, login)
    if d.startswith("usr_block_"):
        login = d[len("usr_block_"):]
        await toggle_user_block(login)
        await q.answer("O'zgartirildi", show_alert=True)
        return await _detail(q, login)
    if d.startswith("usr_logout_"):
        login = d[len("usr_logout_"):]
        await force_logout(login)
        await q.answer("Logout qilindi", show_alert=True)
        return await _detail(q, login)
    if d.startswith("usr_unlinktg_"):
        login = d[len("usr_unlinktg_"):]
        await unlink_telegram(login)
        await q.answer("Telegram uzildi", show_alert=True)
        return await _detail(q, login)
    if d.startswith("usr_xp_"):
        login = d[len("usr_xp_"):]
        context.user_data["target_login"] = login
        await q.message.edit_text(f"💫 <b>{login}</b> XP (+25 / -15):", parse_mode="HTML")
        return ADM_USER_XP_INPUT
    if d.startswith("usr_pts_"):
        login = d[len("usr_pts_"):]
        context.user_data["target_login"] = login
        await q.message.edit_text(f"🎯 <b>{login}</b> Points (+2 / -1):", parse_mode="HTML")
        return ADM_USER_POINTS_INPUT
    if d.startswith("usr_"):
        return await _detail(q, d[4:])
    return ADM_USER_DETAIL


async def _detail(q, login: str) -> int:
    user = await get_user_by_login(login)
    if not user:
        await q.message.edit_text("❌ Topilmadi.", reply_markup=admin_main_kb())
        return ADM_MENU
    s = "🟢" if user.is_active else "🔴"
    a = "👑" if user.is_admin else "👤"
    text = (
        f"{a} <b>{user.school21_login}</b> {s}\n\n"
        f"TG: @{user.telegram_username or '—'} | ID: <code>{user.telegram_id}</code>\n"
        f"Ism: {user.first_name or '—'} {user.last_name or ''}\n"
        f"🏫 {user.campus or '—'} | 📍 {user.current_location or '—'}\n"
        f"🎓 {user.core_program or '—'} | 🛤 {user.main_track or '—'}\n"
        f"⚔️ {user.coalition_name or '—'}\n\n"
        f"⭐ Lv{user.level} | XP: {user.xp}\n"
        f"🎯 Points: {user.peer_points} | 💰 Coins: {user.peer_coins}\n"
        f"🔑 {'🟢' if user.is_logged_in else '🔴'}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Admin-" if user.is_admin else "👑 Admin+", callback_data=f"usr_admin_{login}"),
         InlineKeyboardButton("🔴 Block" if user.is_active else "🟢 Unblock", callback_data=f"usr_block_{login}")],
        [InlineKeyboardButton("💫 XP", callback_data=f"usr_xp_{login}"),
         InlineKeyboardButton("🎯 Points", callback_data=f"usr_pts_{login}")],
        [InlineKeyboardButton("🚪 Logout", callback_data=f"usr_logout_{login}"),
         InlineKeyboardButton("🔓 Unlink TG", callback_data=f"usr_unlinktg_{login}")],
        [InlineKeyboardButton("🔍 Qidirish", callback_data="usr_search"),
         InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")],
    ])
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    return ADM_USER_DETAIL


async def user_xp_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Son kiriting.")
        return ADM_USER_XP_INPUT
    login = context.user_data.pop("target_login", "")
    result = await adjust_user_xp(login, amount)
    await update.message.reply_text(
        f"✅ {login} XP: {result}" if result is not None else "❌ Topilmadi.",
        reply_markup=admin_main_kb(),
    )
    return ADM_MENU


async def user_points_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Son kiriting.")
        return ADM_USER_POINTS_INPUT
    login = context.user_data.pop("target_login", "")
    result = await adjust_user_points(login, amount)
    await update.message.reply_text(
        f"✅ {login} Points: {result}" if result is not None else "❌ Topilmadi.",
        reply_markup=admin_main_kb(),
    )
    return ADM_MENU
