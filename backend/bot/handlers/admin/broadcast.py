"""📣 Broadcast bo'limi — matn, rasm, tugmali xabar, target selection, preview."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.constants import (
    ADM_MENU, ADM_BROADCAST_MENU, ADM_BROADCAST_TEXT, ADM_BROADCAST_PHOTO,
    ADM_BROADCAST_BTN_TEXT, ADM_BROADCAST_BTN_URL, ADM_BROADCAST_TARGET,
    ADM_BROADCAST_CONFIRM,
)
from bot.keyboards import admin_main_kb
from bot.services.user_service import get_user_ids_by_target


async def show_broadcast_menu(q) -> int:
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Matn", callback_data="bcast_text")],
        [InlineKeyboardButton("🖼 Rasm + matn", callback_data="bcast_photo")],
        [InlineKeyboardButton("🔗 Tugmali xabar", callback_data="bcast_button")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")],
    ])
    await q.message.edit_text("📣 <b>Broadcast</b>\n\nTurini tanlang:", parse_mode="HTML", reply_markup=kb)
    return ADM_BROADCAST_MENU


async def broadcast_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "am_back":
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU
    if d == "bcast_text":
        context.user_data["bcast_type"] = "text"
        await q.message.edit_text("📝 Xabar yozing (HTML):")
        return ADM_BROADCAST_TEXT
    if d == "bcast_photo":
        context.user_data["bcast_type"] = "photo"
        await q.message.edit_text("🖼 Rasmni yuboring (caption bilan):")
        return ADM_BROADCAST_PHOTO
    if d == "bcast_button":
        context.user_data["bcast_type"] = "button"
        await q.message.edit_text("📝 Xabar matnini yozing:")
        return ADM_BROADCAST_TEXT
    return ADM_BROADCAST_MENU


async def broadcast_text_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["bcast_text"] = update.message.text.strip()
    if context.user_data.get("bcast_type") == "button":
        await update.message.reply_text("🔗 Tugma matni (masalan: 'Kirish'):")
        return ADM_BROADCAST_BTN_TEXT
    return await _target_selection(update, context)


async def broadcast_photo_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        context.user_data["bcast_photo"] = update.message.photo[-1].file_id
        context.user_data["bcast_text"] = update.message.caption or ""
    else:
        await update.message.reply_text("❌ Rasm yuboring.")
        return ADM_BROADCAST_PHOTO
    return await _target_selection(update, context)


async def broadcast_btn_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["bcast_btn_text"] = update.message.text.strip()
    await update.message.reply_text("🔗 Tugma URL (https://...):")
    return ADM_BROADCAST_BTN_URL


async def broadcast_btn_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ http:// yoki https:// bilan boshlang:")
        return ADM_BROADCAST_BTN_URL
    context.user_data["bcast_btn_url"] = url
    return await _target_selection(update, context)


async def _target_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 Barcha", callback_data="tgt_all"),
         InlineKeyboardButton("🟢 Faol", callback_data="tgt_active")],
        [InlineKeyboardButton("🏫 Toshkent", callback_data="tgt_tashkent"),
         InlineKeyboardButton("🏫 Samarqand", callback_data="tgt_samarkand")],
        [InlineKeyboardButton("👑 Adminlar", callback_data="tgt_admins")],
        [InlineKeyboardButton("❌ Bekor", callback_data="am_back")],
    ])
    await update.effective_chat.send_message("🎯 Kimga?", reply_markup=kb)
    return ADM_BROADCAST_TARGET


async def broadcast_target_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "am_back":
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU

    targets = {"tgt_all": "all", "tgt_active": "active", "tgt_tashkent": "tashkent", "tgt_samarkand": "samarkand", "tgt_admins": "admins"}
    target = targets.get(d, "all")
    context.user_data["bcast_target"] = target
    ids = await get_user_ids_by_target(target)

    text = context.user_data.get("bcast_text", "")
    preview = f"📣 <b>Preview</b>\n\n🎯 {target} ({len(ids)} ta)\n📝 <i>{text[:80]}...</i>" if len(text) > 80 else f"📣 <b>Preview</b>\n\n🎯 {target} ({len(ids)} ta)\n📝 <i>{text}</i>"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 Test (o'zimga)", callback_data="bcast_preview")],
        [InlineKeyboardButton("✅ Yuborish", callback_data="bcast_send"),
         InlineKeyboardButton("❌ Bekor", callback_data="bcast_cancel")],
    ])
    await q.message.edit_text(preview, parse_mode="HTML", reply_markup=kb)
    return ADM_BROADCAST_CONFIRM


async def broadcast_confirm_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "bcast_cancel":
        _cleanup(context)
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU
    if d == "bcast_preview":
        await _send_to(q.from_user.id, context)
        await q.answer("👁 Preview yuborildi", show_alert=True)
        return ADM_BROADCAST_CONFIRM
    if d == "bcast_send":
        target = context.user_data.get("bcast_target", "all")
        ids = await get_user_ids_by_target(target)
        await q.message.edit_text(f"📣 Yuborilmoqda... ({len(ids)})")
        sent = failed = 0
        for uid in ids:
            try:
                await _send_to(uid, context)
                sent += 1
            except Exception:
                failed += 1
        _cleanup(context)
        await q.message.edit_text(
            f"📣 <b>Natija</b>\n\n✅ {sent} | ❌ {failed} | 🎯 {target}",
            parse_mode="HTML", reply_markup=admin_main_kb(),
        )
        return ADM_MENU
    return ADM_BROADCAST_CONFIRM


async def _send_to(uid: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = context.user_data.get("bcast_text", "")
    photo = context.user_data.get("bcast_photo")
    btn_text = context.user_data.get("bcast_btn_text")
    btn_url = context.user_data.get("bcast_btn_url")
    reply_markup = None
    if btn_text and btn_url:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=btn_url)]])
    if photo:
        await context.bot.send_photo(uid, photo=photo, caption=text or None, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await context.bot.send_message(uid, text=text, parse_mode="HTML", reply_markup=reply_markup)


def _cleanup(context: ContextTypes.DEFAULT_TYPE):
    for k in ("bcast_text", "bcast_type", "bcast_photo", "bcast_btn_text", "bcast_btn_url", "bcast_target"):
        context.user_data.pop(k, None)
