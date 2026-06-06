"""Sessiya tugatish FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class FinishStates(StatesGroup):
    confirming_finish = State()
    writing_comment = State()
