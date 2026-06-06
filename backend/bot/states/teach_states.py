"""Slot ochish FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class TeachStates(StatesGroup):
    selecting_direction = State()
    selecting_date = State()
    selecting_start_time = State()
    selecting_end_time = State()
    confirming = State()
