"""Relay chat handleri — faol sessiyali foydalanuvchi xabarlarini uzatadi.

Bu router OXIRGI bo'lib ulanadi: faqat boshqa hech qaysi handler ushlamagan,
FSM holatda bo'lmagan xabarlar bu yerga keladi.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..services.chat_service import RelayChatService

router = Router()


@router.message()
async def relay_message(message: Message, state: FSMContext):
    # FSM holatda bo'lsa (auth/teach/learn/finish), relay qilmaymiz
    if await state.get_state() is not None:
        return
    if message.from_user is None:
        return

    relay = RelayChatService(message.bot)
    session_id = await relay.get_session_for_user(message.from_user.id)
    if session_id is None:
        return  # faol sessiya yo'q — e'tiborsiz qoldiramiz

    await relay.relay(session_id, message.from_user.id, message)
