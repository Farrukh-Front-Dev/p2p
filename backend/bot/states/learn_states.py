"""Slot band qilish FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class LearnStates(StatesGroup):
    selecting_direction = State()
    selecting_slot = State()
    selecting_start = State()  # band qilishda boshlanish vaqti
    selecting_end = State()  # band qilishda tugash vaqti (maks 4 soat)
    confirming = State()
