"""Slot servisi (biznes-logika)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..constants import direction_label
from ..database.models.enums import SlotStatus
from ..database.models.slot import Slot
from ..repositories.slot_repo import SlotRepository
from ..utils.time_utils import now_local


class SlotValidationError(ValueError):
    """Slot validatsiyasi xatosi (foydalanuvchiga ko'rsatish uchun)."""


class SlotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SlotRepository(db)

    async def create_slot(
        self,
        mentor_id: int,
        direction: str,
        start_time: datetime,
        end_time: datetime,
        title: str | None = None,
        description: str | None = None,
    ) -> Slot:
        """Mavjudlik slotini yaratadi (mentor).

        Mentor mavjudlik oynasini belgilaydi: boshlanish (hozirgi vaqtdan keyin)
        va tugash vaqti. Mentor uchun davomiylik cheklovi YO'Q (kun oxirigacha).
        Aniq sessiya vaqtini (maks 4 soat) band qiluvchi (mentee) tanlaydi.
        """
        now = now_local()
        if start_time <= now:
            raise SlotValidationError(
                "Boshlanish vaqti faqat hozirgi vaqtdan keyin bo'lishi mumkin."
            )
        if end_time <= start_time:
            raise SlotValidationError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak.")

        if not title:
            title = f"{direction_label(direction)} sessiyasi"

        return await self.repo.create(
            mentor_id=mentor_id,
            direction=direction,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
        )

    async def get_available_slots(self, direction: str, exclude_user_id: int) -> list[Slot]:
        return await self.repo.get_available_slots(direction, exclude_user_id)

    async def get_slot_by_id(self, slot_id: str | uuid.UUID) -> Slot | None:
        return await self.repo.get_by_id(slot_id)

    async def book_slot(
        self,
        slot_id: str | uuid.UUID,
        mentee_id: int,
        booking_start: datetime,
        booking_end: datetime,
    ) -> bool:
        """Slotni atomik band qiladi va aniq sessiya vaqtini belgilaydi (mentee).

        Mavjudlik oynasini bo'ladi: band qilingan qism shu slotda qoladi,
        qolgan bo'sh vaqt(lar) yangi `open` slot sifatida saqlanadi.

        Misol: oyna 7:00–00:00, band 8:00–9:00 →
          - 8:00–9:00 (booked, shu slot)
          - 7:00–8:00 (yangi open slot)
          - 9:00–00:00 (yangi open slot)
        """
        slot = await self.repo.get_by_id(slot_id)
        if slot is None:
            return False

        # Oyna chegaralarini band qilishdan OLDIN saqlab qolamiz
        window_start = slot.start_time
        window_end = slot.end_time
        direction = slot.direction
        title = slot.title
        mentor_id = slot.mentor_id

        max_minutes = settings.MAX_SESSION_HOURS * 60
        duration = (booking_end - booking_start).total_seconds() / 60
        if duration < 1:
            raise SlotValidationError("Tugash vaqti boshlanishdan keyin bo'lishi kerak.")
        if duration > max_minutes:
            raise SlotValidationError(f"Maksimal davomiylik {settings.MAX_SESSION_HOURS} soat.")
        if booking_start < window_start or booking_end > window_end:
            raise SlotValidationError("Tanlangan vaqt mavjudlik oynasidan tashqarida.")

        booked = await self.repo.book_slot_atomic(slot_id, mentee_id)
        if not booked:
            return False

        # Band qilingan slotni aniq sessiya vaqtiga moslaymiz
        await self.repo.set_times(slot_id, booking_start, booking_end)

        # Qolgan bo'sh vaqtlarni yangi open slot sifatida yaratamiz
        await self._create_leftover_slot(mentor_id, direction, title, window_start, booking_start)
        await self._create_leftover_slot(mentor_id, direction, title, booking_end, window_end)
        return True

    async def _create_leftover_slot(
        self,
        mentor_id: int,
        direction: str,
        title: str | None,
        start: datetime,
        end: datetime,
    ) -> None:
        """Bo'lingan oynaning qolgan qismini yangi open slot qilib yaratadi.

        Juda qisqa (1 qadamdan kam) qoldiqlar e'tiborga olinmaydi.
        """
        min_minutes = 30  # vaqt qadami; bundan qisqa qoldiq slot ochilmaydi
        if (end - start).total_seconds() / 60 < min_minutes:
            return
        await self.repo.create(
            mentor_id=mentor_id,
            direction=direction,
            title=title,
            start_time=start,
            end_time=end,
        )

    async def cancel_slot(self, slot_id: str | uuid.UUID, mentor_id: int) -> dict | None:
        """Slotni mentor tomonidan bekor qiladi.

        Agar slot band qilingan bo'lsa (booked/reminded), mentee'ga 1 tanga
        qaytariladi. Qaytaradi: {refunded_mentee_id, direction} yoki None.
        """
        from .coin_service import CoinService

        slot = await self.repo.get_by_id(slot_id)
        if slot is None or slot.mentor_id != mentor_id:
            return None
        # Eng so'nggi holatni o'qish uchun obyektni yangilaymiz (atomik UPDATE'lardan keyin
        # identity-map'dagi qiymatlar eskirgan bo'lishi mumkin)
        await self.db.refresh(slot)

        # Atributlarni UPDATE'dan oldin saqlab qolamiz (UPDATE ularni expire qiladi)
        mentee_id = slot.mentee_id
        direction = slot.direction
        start_time = slot.start_time
        end_time = slot.end_time

        prev_status = await self.repo.cancel_slot_atomic(slot_id, mentor_id)
        if prev_status is None:
            return None

        refunded_mentee_id = None
        if prev_status in ("booked", "reminded") and mentee_id is not None:
            coin_service = CoinService(self.db)
            await coin_service.refund(
                mentee_id, 1, slot_id=slot_id, description="slot cancelled refund"
            )
            refunded_mentee_id = mentee_id

        return {
            "refunded_mentee_id": refunded_mentee_id,
            "direction": direction,
            "start_time": start_time,
            "end_time": end_time,
        }

    async def get_user_slots(self, user_id: int) -> list[Slot]:
        return await self.repo.get_user_slots(user_id)

    async def update_slot(
        self,
        slot_id: str | uuid.UUID,
        mentor_id: int,
        direction: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Slot | None:
        """Ochiq (open) slotni tahrirlaydi (faqat egasi).

        Faqat hali band qilinmagan slotlar tahrirlanadi. Vaqt o'zgartirilsa,
        validatsiya qo'llanadi. Qaytaradi: yangilangan slot yoki None.
        """
        slot = await self.repo.get_by_id(slot_id)
        if slot is None or slot.mentor_id != mentor_id:
            return None
        if slot.status != SlotStatus.OPEN.value:
            return None

        new_start = start_time or slot.start_time
        new_end = end_time or slot.end_time
        now = now_local()
        if new_start <= now:
            raise SlotValidationError(
                "Boshlanish vaqti faqat hozirgi vaqtdan keyin bo'lishi mumkin."
            )
        if new_end <= new_start:
            raise SlotValidationError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak.")

        new_direction = direction or slot.direction
        await self.repo.update_open_slot(
            slot_id, direction=new_direction, start_time=new_start, end_time=new_end
        )
        return await self.repo.get_by_id(slot_id)
