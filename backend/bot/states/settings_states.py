"""Sozlamalar FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    selecting_language = State()
