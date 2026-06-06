"""Ro'yxatdan o'tish FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    waiting_login = State()
    waiting_password = State()
    selecting_directions = State()
