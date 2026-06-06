"""Slot repository (atomik operatsiyalar bilan)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.enums import SlotStatus
from ..database.models.slot import Slot
from ..utils.time_utils import now_local


def _to_uuid(slot_id: str | uuid.UUID) -> uuid.UUID:
    return slot_id if isinstance(slot_id, uuid.UUID) else uuid.UUID(str(slot_id))


class SlotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, slot_id: str | uuid.UUID) -> Slot | None:
        return await self.db.get(Slot, _to_uuid(slot_id))

    async def create(self, **kwargs) -> Slot:
        slot = Slot(**kwargs)
        self.db.add(slot)
        await self.db.flush()
        return slot

    async def get_available_slots(
        self, direction: str, exclude_user_id: int, limit: int = 20
    ) -> list[Slot]:
        """Faqat ochiq (open) va boshqa foydalanuvchiga tegishli slotlar."""
        now = now_local()
        result = await self.db.execute(
            select(Slot)
            .where(
                Slot.direction == direction,
                Slot.status == SlotStatus.OPEN.value,
                Slot.mentor_id != exclude_user_id,
                Slot.start_time > now,
            )
            .order_by(Slot.start_time.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_slots(self, user_id: int) -> list[Slot]:
        """Foydalanuvchining mentor yoki mentee sifatidagi slotlari."""
        result = await self.db.execute(
            select(Slot)
            .where((Slot.mentor_id == user_id) | (Slot.mentee_id == user_id))
            .order_by(Slot.start_time.asc())
        )
        return list(result.scalars().all())

    async def book_slot_atomic(self, slot_id: str | uuid.UUID, mentee_id: int) -> bool:
        """Slotni atomik band qiladi.

        Faqat status='open' VA mentor_id != mentee_id bo'lganda muvaffaqiyatli.
        Parallel urinishlarda faqat bittasi True qaytaradi (Property 3, 4).
        """
        stmt = (
            update(Slot)
            .where(
                Slot.id == _to_uuid(slot_id),
                Slot.status == SlotStatus.OPEN.value,
                Slot.mentor_id != mentee_id,
            )
            .values(status=SlotStatus.BOOKED.value, mentee_id=mentee_id)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount == 1

    async def update_status(self, slot_id: str | uuid.UUID, status: SlotStatus | str) -> None:
        status_value = status.value if isinstance(status, SlotStatus) else status
        await self.db.execute(
            update(Slot)
            .where(Slot.id == _to_uuid(slot_id))
            .values(status=status_value)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.flush()

    async def release_slot(self, slot_id: str | uuid.UUID) -> None:
        """Band qilingan slotni qaytadan ochiq (open) holatga qaytaradi.

        Coin ayirish muvaffaqiyatsiz bo'lganda kompensatsiya uchun.
        """
        await self.db.execute(
            update(Slot)
            .where(Slot.id == _to_uuid(slot_id))
            .values(status=SlotStatus.OPEN.value, mentee_id=None)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.flush()

    async def cancel_slot_atomic(self, slot_id: str | uuid.UUID, mentor_id: int) -> str | None:
        """Slotni atomik bekor qiladi (faqat egasi va bekor qilinadigan holatda).

        Faqat status ∈ {open, booked, reminded} VA mentor_id mos kelganda.
        Bekor qilishdan oldingi statusni qaytaradi (mentee bo'lsa, coin qaytarish
        uchun kerak) yoki None (bekor qilib bo'lmadi).
        """
        slot = await self.db.get(Slot, _to_uuid(slot_id))
        if slot is None or slot.mentor_id != mentor_id:
            return None
        # Identity-map'dagi qiymat eskirgan bo'lishi mumkin — yangilaymiz
        await self.db.refresh(slot)
        # Statusni UPDATE'dan OLDIN saqlab qolamiz (UPDATE atributni expire qiladi)
        prev_status = slot.status
        cancellable = {
            SlotStatus.OPEN.value,
            SlotStatus.BOOKED.value,
            SlotStatus.REMINDED.value,
        }
        stmt = (
            update(Slot)
            .where(
                Slot.id == _to_uuid(slot_id),
                Slot.mentor_id == mentor_id,
                Slot.status.in_(cancellable),
            )
            .values(status=SlotStatus.CANCELLED.value)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        if result.rowcount != 1:
            return None
        return prev_status  # bekor qilishdan oldingi status

    async def set_chat_group(self, slot_id: str | uuid.UUID, chat_group_id: int) -> None:
        await self.db.execute(
            update(Slot)
            .where(Slot.id == _to_uuid(slot_id))
            .values(chat_group_id=chat_group_id)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.flush()

    async def set_times(
        self,
        slot_id: str | uuid.UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Slot boshlanish va tugash vaqtini yangilaydi (mentee band qilganda)."""
        await self.db.execute(
            update(Slot)
            .where(Slot.id == _to_uuid(slot_id))
            .values(start_time=start_time, end_time=end_time)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.flush()

    async def update_open_slot(
        self,
        slot_id: str | uuid.UUID,
        direction: str,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        """Ochiq slotni tahrirlaydi (faqat status='open' bo'lganda — atomik)."""
        stmt = (
            update(Slot)
            .where(
                Slot.id == _to_uuid(slot_id),
                Slot.status == SlotStatus.OPEN.value,
            )
            .values(direction=direction, start_time=start_time, end_time=end_time)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount == 1

    async def get_slots_for_reminder(self, now: datetime, threshold: datetime) -> list[Slot]:
        """Eslatma yuborilishi kerak: booked, eslatma yuborilmagan, vaqti yaqin."""
        result = await self.db.execute(
            select(Slot).where(
                Slot.status == SlotStatus.BOOKED.value,
                Slot.reminder_sent.is_(False),
                Slot.start_time <= threshold,
                Slot.start_time > now,
            )
        )
        return list(result.scalars().all())

    async def mark_reminder_sent(self, slot_id: str | uuid.UUID) -> bool:
        """Eslatmani atomik belgilaydi (Property 7: ko'pi bilan bir marta).

        Faqat reminder_sent=False bo'lganda True qaytaradi.
        """
        stmt = (
            update(Slot)
            .where(
                Slot.id == _to_uuid(slot_id),
                Slot.reminder_sent.is_(False),
            )
            .values(
                reminder_sent=True,
                reveal_sent=True,
                status=SlotStatus.REMINDED.value,
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount == 1

    async def get_slots_to_start(self, now: datetime) -> list[Slot]:
        """Boshlanishi kerak bo'lgan slotlar: reminded, vaqti kelgan."""
        result = await self.db.execute(
            select(Slot).where(
                Slot.status == SlotStatus.REMINDED.value,
                Slot.start_time <= now,
            )
        )
        return list(result.scalars().all())
