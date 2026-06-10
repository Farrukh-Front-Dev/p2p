"""Bot command handlers — subscription check + School21 login onboarding."""
from __future__ import annotations

import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes

from bot.config import settings

logger = logging.getLogger(__name__)

# Mini App URL: production da HTTPS domeningiz, lokal testda oddiy havola
WEBAPP_URL = settings.TELEGRAM_WEBHOOK_URL.replace("/bot/webhook", "").rstrip("/")
if not WEBAPP_URL or "yourdomain" in WEBAPP_URL:
    # lokal/test muhiti — WebApp o'rniga oddiy havola ko'rsatamiz
    WEBAPP_URL = None


# ─── subscription check ──────────────────────────────────────────────────────

async def _is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    channel = settings.TELEGRAM_REQUIRED_CHANNEL
    if not channel:
        return True
    try:
        member = await context.bot.get_chat_member(channel, update.effective_user.id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except Exception:
        return True  # kanal topilmasa bloklama


# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info("/start from %s (%s)", user.id, user.username)

    if not await _is_subscribed(update, context):
        channel = settings.TELEGRAM_REQUIRED_CHANNEL
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Kanalga obuna", url=f"https://t.me/{channel.lstrip('@')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")],
        ])
        await update.message.reply_text(
            "❗ Davom etish uchun avval kanalga obuna bo'ling.", reply_markup=kb
        )
        return

    if WEBAPP_URL:
        from telegram import WebAppInfo
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 P2P Platformani ochish", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await update.message.reply_text(
            f"Salom, {user.first_name}! 👋\nP2P platformaga xush kelibsiz.",
            reply_markup=kb,
        )
    else:
        # Lokal/test muhiti — WebApp URL yo'q
        # Foydalanuvchiga test uchun kerakli ma'lumotlarni ko'rsatamiz
        await update.message.reply_text(
            f"Salom, {user.first_name}! 👋\n\n"
            f"🔧 <b>Test rejimi</b>\n\n"
            f"Sizning ma'lumotlaringiz:\n"
            f"├ Telegram ID: <code>{user.id}</code>\n"
            f"├ Username: @{user.username or '—'}\n"
            f"└ Ism: {user.first_name}\n\n"
            f"🛠 Test <code>init_data</code> olish uchun terminalda:\n"
            f"<pre>python3 scripts/gen_init_data.py \\\n"
            f"  --id {user.id} \\\n"
            f"  --username {user.username or 'username'} \\\n"
            f"  --first {user.first_name}</pre>\n\n"
            f"📖 Swagger: http://localhost:8001/docs",
            parse_mode="HTML",
        )


# ─── /webapp ─────────────────────────────────────────────────────────────────

async def webapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if WEBAPP_URL:
        from telegram import WebAppInfo
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Ochish", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await update.message.reply_text("Mini App:", reply_markup=kb)
    else:
        await update.message.reply_text(
            "⚠️ Mini App URL hali sozlanmagan.\n"
            ".env da TELEGRAM_WEBHOOK_URL ni to'g'ri domen bilan o'rnating."
        )


# ─── /profile ────────────────────────────────────────────────────────────────

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"👤 <b>Telegram profil</b>\n"
        f"ID: <code>{user.id}</code>\n"
        f"Username: @{user.username or '—'}\n"
        f"Ism: {user.first_name}",
        parse_mode="HTML",
    )


# ─── /slots ──────────────────────────────────────────────────────────────────

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📅 Slotlarni ko'rish uchun Mini App dan foydalaning.\n/webapp"
    )


# ─── /help ───────────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 <b>Komandalar ro'yxati</b>\n\n"
        "/start   — Boshlash\n"
        "/webapp  — Mini App havolasi\n"
        "/profile — Telegram profil\n"
        "/slots   — Slotlar\n"
        "/help    — Yordam\n"
        "/cancel  — Bekor qilish",
        parse_mode="HTML",
    )


# ─── /cancel ─────────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("❌ Joriy amal bekor qilindi.")
