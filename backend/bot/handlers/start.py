"""Bot oqimi:

1. Foydalanuvchi saytdan login qiladi → need_telegram → temp_token oladi
2. Sayt "Botga o'tish" tugmasini ko'rsatadi: https://t.me/bot?start={temp_token}
3. Foydalanuvchi botga /start {temp_token} bilan keladi
4. Bot: obuna tekshiradi → OTP kod beradi
5. Foydalanuvchi kodni saytga kiritadi → /verify-code

Bot hech qachon S21 login/parol so'ramaydi!
Oddiy /start (temp_token siz) — faqat webapp tugmasi yoki "Saytdan login qiling" deydi.
"""
from __future__ import annotations

import logging
import secrets

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    CallbackQueryHandler, CommandHandler, ContextTypes,
    ConversationHandler,
)

from bot.constants import REG_CHECK_SUBSCRIPTION
from bot.services.channel_service import get_active_channels
from bot.services.settings_service import get_settings

logger = logging.getLogger(__name__)

OTP_TTL = 300  # 5 daqiqa
OTP_PREFIX = "otp:"


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_user_by_tg(telegram_id: int):
    from sqlalchemy import select
    from app.db.base import AsyncSessionLocal
    from app.db.models.user import User
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )).scalar_one_or_none()


async def _check_subscriptions(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    s = await get_settings()
    if not s.subscription_enabled:
        return True, []
    channels = await get_active_channels()
    if not channels:
        return True, []
    unsubscribed = []
    for ch in channels:
        try:
            cid = int(ch.channel_id) if ch.channel_id.lstrip("-").isdigit() else ch.channel_id
            m = await context.bot.get_chat_member(cid, user_id)
            if m.status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                unsubscribed.append(ch)
        except Exception:
            unsubscribed.append(ch)
    return len(unsubscribed) == 0, unsubscribed


async def _webapp_keyboard():
    s = await get_settings()
    url = s.webapp_url
    if not url:
        return None
    from telegram import WebAppInfo
    return InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Platformaga kirish", web_app=WebAppInfo(url=url))]])


async def _generate_otp(user_id: str, telegram_id: int) -> str:
    from app.services.cache import redis_client
    code = f"{secrets.randbelow(900000) + 100000}"
    # Format: "code:telegram_id" — faqat shu telegram_id bilan tasdiqlash mumkin
    await redis_client.setex(f"{OTP_PREFIX}{user_id}", OTP_TTL, f"{code}:{telegram_id}")
    return code


async def _get_user_id_from_temp_token(temp_token: str) -> str | None:
    from app.services.cache import redis_client
    return await redis_client.get(f"temp:{temp_token}")


async def _show_sub_buttons(update: Update, unsub, context) -> int:
    from app.services.cache import redis_client
    buttons = []
    for ch in unsub:
        link = ch.invite_link
        if not link:
            cached = await redis_client.get(f"invite:{ch.channel_id}")
            if cached:
                link = cached
            else:
                try:
                    cid = int(ch.channel_id) if ch.channel_id.lstrip("-").isdigit() else ch.channel_id
                    invite = await context.bot.export_chat_invite_link(cid)
                    link = invite
                    await redis_client.setex(f"invite:{ch.channel_id}", 3600, invite)
                except Exception:
                    link = None
        if link:
            buttons.append([InlineKeyboardButton(f"📢 {ch.title}", url=link)])
    buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
    await update.effective_chat.send_message(
        f"📢 {len(unsub)} ta kanalga obuna bo'ling.\n\n"
        "Obuna bo'lgach \"✅ Tekshirish\" bosing.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return REG_CHECK_SUBSCRIPTION


# ── Main handler ──────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    /start {temp_token} — saytdan kelgan foydalanuvchi (obuna → kod)
    /start              — oddiy kirish (webapp yoki "saytdan login qiling")
    """
    user = update.effective_user
    logger.info("/start from %s (%s)", user.id, user.username)

    s = await get_settings()
    if s.maintenance_mode:
        await update.message.reply_text(s.maintenance_message or "🔧 Texnik ishlar.")
        return ConversationHandler.END

    # deep link: /start {temp_token}
    args = context.args
    temp_token = args[0] if args else None

    if temp_token:
        # Saytdan kelgan — temp_token ni tekshirish
        user_id = await _get_user_id_from_temp_token(temp_token)
        if not user_id:
            await update.message.reply_text(
                "❌ Havola muddati o'tgan yoki noto'g'ri.\n\n"
                "Saytda qaytadan login qiling."
            )
            return ConversationHandler.END

        # temp_token ni context da saqlaymiz (obuna dan keyin kod berish uchun)
        context.user_data["temp_token"] = temp_token
        context.user_data["link_user_id"] = user_id

        # Obuna tekshirish
        ok, unsub = await _check_subscriptions(user.id, context)
        if not ok:
            return await _show_sub_buttons(update, unsub, context)

        # Obuna OK — kod berish
        return await _generate_and_show_code(update, context)

    # Oddiy /start (temp_token yo'q) — mavjud user bo'lsa webapp, bo'lmasa yo'naltirish
    db_user = await _get_user_by_tg(user.id)
    if db_user and db_user.is_logged_in:
        kb = await _webapp_keyboard()
        if kb:
            await update.message.reply_text(
                f"👋 Salom, {user.first_name}!", reply_markup=kb)
        else:
            await update.message.reply_text(f"👋 Salom, {user.first_name}!\n/help — yordam")
        return ConversationHandler.END

    # Telegram bog'lanmagan yoki logout — saytga yo'naltirish
    s = await get_settings()
    webapp_url = s.webapp_url
    if webapp_url:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Saytga o'tish", url=webapp_url)]
        ])
        await update.message.reply_text(
            "👋 <b>P2P Platformaga xush kelibsiz!</b>\n\n"
            "Tizimga kirish uchun saytda login qiling:",
            parse_mode="HTML", reply_markup=kb,
        )
    else:
        await update.message.reply_text(
            "👋 <b>P2P Platformaga xush kelibsiz!</b>\n\n"
            "Tizimga kirish uchun saytda login qiling.\n"
            "Sayt tayyor bo'lganda sizga havola yuboriladi.",
            parse_mode="HTML",
        )
    return ConversationHandler.END


async def check_sub_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Obuna tekshirish tugmasi."""
    q = update.callback_query
    await q.answer()

    ok, unsub = await _check_subscriptions(q.from_user.id, context)
    if ok:
        await q.message.edit_text("✅ Obuna tasdiqlandi!")
        return await _generate_and_show_code(update, context)

    await q.answer(f"❌ {len(unsub)} ta kanal qoldi!", show_alert=True)
    return REG_CHECK_SUBSCRIPTION


async def _generate_and_show_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """OTP kod generatsiya qilish va ko'rsatish."""
    user_id = context.user_data.get("link_user_id")
    tg_user = update.effective_user

    if not user_id:
        await update.effective_chat.send_message("❌ Xato. Saytda qaytadan login qiling.")
        return ConversationHandler.END

    # telegram_id ni user ga bog'lash (hali bog'lanmagan bo'lsa)
    from sqlalchemy import select
    from app.db.base import AsyncSessionLocal
    from app.db.models.user import User
    import uuid

    async with AsyncSessionLocal() as db:
        user = await db.get(User, uuid.UUID(user_id))
        if not user:
            await update.effective_chat.send_message("❌ Foydalanuvchi topilmadi.")
            return ConversationHandler.END

        # Tekshirish: bu telegram_id boshqa userga bog'langanmi?
        existing = (await db.execute(
            select(User).where(
                User.telegram_id == tg_user.id,
                User.id != user.id,
            )
        )).scalar_one_or_none()

        if existing:
            await update.effective_chat.send_message(
                "❌ <b>Bu Telegram akkaunt allaqachon boshqa School21 hisobga bog'langan:</b>\n"
                f"<code>{existing.school21_login}</code>\n\n"
                "Har bir Telegram akkaunt faqat bitta School21 hisobga bog'lanishi mumkin.",
                parse_mode="HTML",
            )
            return ConversationHandler.END

        # Telegram ma'lumotlarini yangilash (har doim — yangi bog'lash yoki qayta bog'lash)
        user.telegram_id = tg_user.id
        user.telegram_username = tg_user.username
        user.first_name = tg_user.first_name or user.first_name
        if tg_user.last_name:
            user.last_name = tg_user.last_name
        await db.commit()

    # OTP generatsiya — faqat shu user_id va telegram_id uchun
    code = await _generate_otp(user_id, tg_user.id)

    s = await get_settings()
    webapp_url = s.webapp_url

    text = (
        "✅ <b>Telegram tasdiqlandi!</b>\n\n"
        f"🔑 Sizning kodingiz:\n\n"
        f"<code>{code}</code>\n\n"
        f"⏱ Kod 5 daqiqa amal qiladi.\n"
        f"Saytdagi \"Kodni kiriting\" maydoniga yozing."
    )
    kb = None
    if webapp_url:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Saytga qaytish", url=webapp_url)]])

    await update.effective_chat.send_message(text, parse_mode="HTML", reply_markup=kb)

    # Cleanup
    context.user_data.pop("temp_token", None)
    context.user_data.pop("link_user_id", None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Bekor. /start")
    return ConversationHandler.END


# ── Oddiy komandalar ──────────────────────────────────────────────────────────

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 <b>Komandalar</b>\n\n"
        "/start   — Boshlash\n"
        "/webapp  — Platformaga kirish\n"
        "/admin   — Admin panel\n"
        "/help    — Yordam",
        parse_mode="HTML",
    )


async def webapp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    kb = await _webapp_keyboard()
    if kb:
        await update.message.reply_text("🚀 Platformaga kirish:", reply_markup=kb)
    else:
        await update.message.reply_text("⚠️ Mini App hali tayyor emas.")


# ── ConversationHandler ───────────────────────────────────────────────────────

def get_start_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REG_CHECK_SUBSCRIPTION: [
                CallbackQueryHandler(check_sub_cb, pattern="^check_sub$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )
