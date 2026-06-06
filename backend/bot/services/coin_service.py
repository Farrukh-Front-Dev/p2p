"""Coin (tanga) servisi — atomik va idempotent."""

from __future__ import annotations

import uuid

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database.models.enums import TransactionType
from ..database.models.session import Session
from ..database.models.user import User
from ..repositories.transaction_repo import TransactionRepository


class CoinService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tx_repo = TransactionRepository(db)

    async def deduct(
        self,
        user_id: int,
        amount: int,
        reason: str = "spend_learn",
        slot_id: uuid.UUID | str | None = None,
        session_id: uuid.UUID | str | None = None,
    ) -> bool:
        """Atomik tanga ayirish.

        Faqat coins >= amount bo'lganda muvaffaqiyatli (Property 1).
        Muvaffaqiyatda transactions yozuvi qo'shadi (Property 9).
        """
        if amount <= 0:
            raise ValueError("amount must be positive")

        stmt = (
            update(User)
            .where(User.id == user_id, User.coins >= amount)
            .values(coins=User.coins - amount)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        if result.rowcount != 1:
            return False

        await self.tx_repo.create(
            user_id=user_id,
            amount=-amount,
            type=reason,
            slot_id=slot_id,
            session_id=session_id,
            description=f"deduct {amount} ({reason})",
        )
        return True

    async def reward_mentor(self, session: Session) -> bool:
        """Mentorga sessiya uchun tanga beradi (idempotent + cap).

        Property 2: coins <= max_coins. Property 5: faqat bir marta.
        """
        if session.coins_transferred:
            return False

        user = await self.db.get(User, session.mentor_id)
        if user is None:
            return False

        before = user.coins
        user.coins = min(user.coins + settings.COIN_PER_SESSION, user.max_coins)
        session.coins_transferred = True
        await self.db.flush()

        gained = user.coins - before
        if gained > 0:
            await self.tx_repo.create(
                user_id=session.mentor_id,
                amount=gained,
                type=TransactionType.EARN_TEACH,
                session_id=session.id,
                slot_id=session.slot_id,
                description="reward for teaching",
            )
        return True

    async def add_bonus(self, user_id: int, amount: int, description: str = "bonus") -> bool:
        """Admin bonusi (cap bilan)."""
        user = await self.db.get(User, user_id)
        if user is None:
            return False
        before = user.coins
        user.coins = min(user.coins + amount, user.max_coins)
        await self.db.flush()
        gained = user.coins - before
        if gained > 0:
            await self.tx_repo.create(
                user_id=user_id,
                amount=gained,
                type=TransactionType.BONUS,
                description=description,
            )
        return True

    async def refund(
        self,
        user_id: int,
        amount: int,
        slot_id: uuid.UUID | str | None = None,
        description: str = "refund",
    ) -> bool:
        """Tangani qaytaradi (masalan, slot bekor qilinganda mentee'ga).

        Cap'dan oshmaydi (Property 2). Tranzaksiya yoziladi (Property 9).
        """
        if amount <= 0:
            raise ValueError("amount must be positive")
        user = await self.db.get(User, user_id)
        if user is None:
            return False
        before = user.coins
        user.coins = min(user.coins + amount, user.max_coins)
        await self.db.flush()
        gained = user.coins - before
        if gained > 0:
            await self.tx_repo.create(
                user_id=user_id,
                amount=gained,
                type=TransactionType.BONUS,
                slot_id=slot_id,
                description=description,
            )
        return True
