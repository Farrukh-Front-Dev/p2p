"""Slot endpointlari (ochish, ko'rish, band qilish, bekor qilish)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.user import User
from ..services.coin_service import CoinService
from ..services.slot_service import SlotService, SlotValidationError
from .deps import get_current_user, get_db_session
from .schemas import (
    BookSlotRequest,
    CreateSlotRequest,
    MessageResponse,
    SlotOut,
)
from .serializers import slot_to_out

router = APIRouter(prefix="/api/slots", tags=["slots"])


@router.get("", response_model=list[SlotOut])
async def list_available_slots(
    direction: str,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Yo'nalish bo'yicha mavjud (open) slotlar — anonim (mentor ko'rinmaydi)."""
    service = SlotService(db)
    slots = await service.get_available_slots(direction=direction, exclude_user_id=current.id)
    # Anonimlik: mentor identifikatori chiqarilmaydi (is_mine=False)
    return [slot_to_out(s) for s in slots]


@router.get("/mine", response_model=list[SlotOut])
async def my_slots(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = SlotService(db)
    slots = await service.get_user_slots(current.id)
    return [slot_to_out(s, current.id) for s in slots]


@router.post("", response_model=SlotOut)
async def create_slot(
    body: CreateSlotRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Mentor sifatida mavjudlik slotini ochish."""
    service = SlotService(db)
    try:
        slot = await service.create_slot(
            mentor_id=current.id,
            direction=body.direction,
            start_time=body.start_time,
            end_time=body.end_time,
        )
    except SlotValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await db.flush()
    return slot_to_out(slot, current.id)


@router.post("/{slot_id}/book", response_model=MessageResponse)
async def book_slot(
    slot_id: str,
    body: BookSlotRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Slotni band qilish (mentee). 1 tanga sarflaydi."""
    if current.coins < 1:
        raise HTTPException(status_code=402, detail="Yetarli tanga yo'q")

    service = SlotService(db)
    coin_service = CoinService(db)
    try:
        booked = await service.book_slot(slot_id, current.id, body.start_time, body.end_time)
    except SlotValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not booked:
        raise HTTPException(status_code=409, detail="Slot allaqachon band yoki o'zingiznikidir")

    deducted = await coin_service.deduct(current.id, 1, reason="spend_learn", slot_id=slot_id)
    if not deducted:
        await service.repo.release_slot(slot_id)
        raise HTTPException(status_code=402, detail="Yetarli tanga yo'q")

    return MessageResponse(detail="Slot band qilindi")


@router.delete("/{slot_id}", response_model=MessageResponse)
async def cancel_slot(
    slot_id: str,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Slotni bekor qilish (faqat mentor). Band qilingan bo'lsa mentee'ga refund."""
    service = SlotService(db)
    result = await service.cancel_slot(slot_id, mentor_id=current.id)
    if result is None:
        raise HTTPException(status_code=400, detail="Slotni bekor qilib bo'lmadi")
    detail = "Slot bekor qilindi"
    if result.get("refunded_mentee_id"):
        detail += " (band qiluvchiga tanga qaytarildi)"
    return MessageResponse(detail=detail)
