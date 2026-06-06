"""Transaction repository (audit izi uchun)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.enums import TransactionType
from ..database.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        amount: int,
        type: TransactionType | str,
        slot_id: uuid.UUID | str | None = None,
        session_id: uuid.UUID | str | None = None,
        description: str | None = None,
    ) -> Transaction:
        type_value = type.value if isinstance(type, TransactionType) else type
        tx = Transaction(
            user_id=user_id,
            amount=amount,
            type=type_value,
            slot_id=slot_id,
            session_id=session_id,
            description=description,
        )
        self.db.add(tx)
        await self.db.flush()
        return tx

    async def get_by_user(self, user_id: int, limit: int = 50) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
