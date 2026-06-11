"""📢 Kanallar bo'limi — CRUD, toggle, edit."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.constants import (
    ADM_CHANNELS_LIST, ADM_CHANNEL_ADD_ID, ADM_CHANNEL_ADD_TITLE,
    ADM_CHANNEL_ADD_LINK, ADM_CHANNEL_DETAIL, ADM_CHANNEL_EDIT,
    ADM_CHANNEL_EDIT_INPUT, ADM_MENU,
)
from bot.keyboards import admin_main_kb
from bot.services.channel_service import (
    get_all_channels, get_channel, add_channel, toggle_channel,
    delete_channel, update_channel,
)


async def channels_list_cb(q, context) -> int:
    channels = await get_all_channels()
    text = "📢 <b>Majburiy obuna kanallari</b>\n\n"
    if not channels:
        text += "<i>Kanal yo'q</i>"
    for ch in channels:
        icon = "🟢" if ch.is_active else "⏸"
        text += f"{icon} <b>{ch.title}</b>\n   <code>{ch.channel_id}</code>\n"
    buttons = [
        [InlineKeyboardButton(f"{'🟢' if c.is_active else '⏸'} {c.title}", callback_data=f"ch_{c.id}")]
        for c in channels
    ]
    buttons.append([InlineKeyboardButton("➕ Kanal qo'shish", callback_data="ch_add")])
    buttons.append([InlineKeyboardButton("◀️ Orqaga", callback_data="am_back")])
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    return ADM_CHANNELS_LIST


async def channels_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "am_back":
        await q.message.edit_text("⚙️ <b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MENU
    if d == "ch_add":
        await q.message.edit_text("📢 Kanal ID yoki @username:\n<i>Masalan: -1001234567890</i>", parse_mode="HTML")
        return ADM_CHANNEL_ADD_ID
    if d.startswith("ch_"):
        return await _show_detail(q, d[3:], context)
    return ADM_CHANNELS_LIST


async def _show_detail(q, ch_id: str, context) -> int:
    ch = await get_channel(ch_id)
    if not ch:
        await q.message.edit_text("❌ Topilmadi.", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("◀️", callback_data="ch_back")]]))
        return ADM_CHANNEL_DETAIL
    status = "🟢 Faol" if ch.is_active else "⏸ To'xtatilgan"
    count = "?"
    try:
        cid = int(ch.channel_id) if ch.channel_id.lstrip("-").isdigit() else ch.channel_id
        count = str(await context.bot.get_chat_member_count(cid))
    except Exception:
        pass
    text = (
        f"📢 <b>{ch.title}</b>\n\n"
        f"🆔 <code>{ch.channel_id}</code>\n"
        f"📊 {status}\n👥 A'zolar: {count}\n"
        f"🔗 {ch.invite_link or '(havola yo`q)'}\n"
        f"📅 {ch.created_at.strftime('%Y-%m-%d %H:%M') if ch.created_at else '-'}"
    )
    toggle = InlineKeyboardButton(
        "⏸ To'xtatish" if ch.is_active else "▶️ Faollashtirish",
        callback_data=f"chd_toggle_{ch.id}",
    )
    kb = InlineKeyboardMarkup([
        [toggle],
        [InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"chd_edit_{ch.id}")],
        [InlineKeyboardButton("🗑 Butunlay o'chirish", callback_data=f"chd_del_{ch.id}")],
        [InlineKeyboardButton("◀️ Kanallar", callback_data="ch_back")],
    ])
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    return ADM_CHANNEL_DETAIL


async def channel_detail_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "ch_back":
        return await channels_list_cb(q, context)
    if d.startswith("chd_toggle_"):
        cid = d[len("chd_toggle_"):]
        await toggle_channel(cid)
        return await _show_detail(q, cid, context)
    if d.startswith("chd_del_"):
        cid = d[len("chd_del_"):]
        await delete_channel(cid)
        await q.answer("🗑 O'chirildi", show_alert=True)
        return await channels_list_cb(q, context)
    if d.startswith("chd_edit_"):
        cid = d[len("chd_edit_"):]
        context.user_data["edit_ch_id"] = cid
        ch = await get_channel(cid)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Nom", callback_data="che_title")],
            [InlineKeyboardButton("🔗 Havola", callback_data="che_link")],
            [InlineKeyboardButton("🆔 ID", callback_data="che_id")],
            [InlineKeyboardButton("◀️ Orqaga", callback_data=f"che_back_{cid}")],
        ])
        await q.message.edit_text(
            f"✏️ <b>{ch.title if ch else '?'}</b> — nima o'zgartirilsin?",
            parse_mode="HTML", reply_markup=kb,
        )
        return ADM_CHANNEL_EDIT
    return ADM_CHANNEL_DETAIL


# ── Edit ──────────────────────────────────────────────────────────────────────

async def channel_edit_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    if d.startswith("che_back_"):
        return await _show_detail(q, d[len("che_back_"):], context)
    prompts = {"che_title": "📝 Yangi nom:", "che_link": "🔗 Yangi havola (/skip):", "che_id": "🆔 Yangi ID:"}
    fields = {"che_title": "title", "che_link": "invite_link", "che_id": "channel_id"}
    if d in prompts:
        context.user_data["edit_field"] = fields[d]
        await q.message.edit_text(prompts[d])
        return ADM_CHANNEL_EDIT_INPUT
    return ADM_CHANNEL_EDIT


async def channel_edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    cid = context.user_data.pop("edit_ch_id", "")
    field = context.user_data.pop("edit_field", "")
    if not cid or not field:
        await update.message.reply_text("❌ Xato.", reply_markup=admin_main_kb())
        return ADM_MENU
    val = None if text == "/skip" else text
    ch = await update_channel(cid, **{field: val})
    msg = f"✅ <b>{ch.title}</b> yangilandi." if ch else "❌ Topilmadi."
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=admin_main_kb())
    return ADM_MENU


# ── Add ───────────────────────────────────────────────────────────────────────

async def channel_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_ch_id"] = update.message.text.strip()
    await update.message.reply_text("📝 Kanal nomini kiriting:")
    return ADM_CHANNEL_ADD_TITLE


async def channel_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_ch_title"] = update.message.text.strip()
    await update.message.reply_text("🔗 Invite havola (/skip):", parse_mode="HTML")
    return ADM_CHANNEL_ADD_LINK


async def channel_add_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    link = None if text == "/skip" else text
    cid = context.user_data.pop("new_ch_id", "")
    title = context.user_data.pop("new_ch_title", "")
    await add_channel(cid, title, link)
    await update.message.reply_text(f"✅ <b>{title}</b> qo'shildi.", parse_mode="HTML", reply_markup=admin_main_kb())
    return ADM_MENU
