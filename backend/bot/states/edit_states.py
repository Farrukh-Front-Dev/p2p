"""Slot tahrirlash FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class EditStates(StatesGroup):
    choosing_field = State()
    selecting_direction = State()
    selecting_date = State()
    selecting_start_time = State()
    selecting_end_time = State()
