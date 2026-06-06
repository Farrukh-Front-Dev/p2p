"""Sessiya endpointlari (faol sessiya, yakunlash)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.user import User
from ..repositories.slot_repo import SlotRepository
from ..services.session_service import SessionService
from .deps import get_current_user, get_db_session
from .schemas import FinishSessionRequest, SessionOut

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


async def _session_to_out(db, session, current_user_id: int) -> SessionOut:
    slot_repo = SlotRepository(db)
    slot = await slot_repo.get_by_id(session.slot_id)
    role = (
        "mentor"
        if session.mentor_id == current_user_id
        else ("mentee" if session.mentee_id == current_user_id else None)
    )
    return SessionOut(
        id=str(session.id),
        slot_id=str(session.slot_id),
        direction=slot.direction if slot else None,
        start_time=slot.start_time if slot else None,
        end_time=slot.end_time if slot else None,
        status=session.status,
        mentor_confirmed=session.mentor_confirmed,
        mentee_confirmed=session.mentee_confirmed,
        role=role,
    )


@router.get("/active", response_model=SessionOut | None)
async def active_session(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Joriy foydalanuvchining faol sessiyasi (yoki null)."""
    service = SessionService(db)
    session = await service.get_active_session_by_user(current.id)
    if session is None:
        return None
    return await _session_to_out(db, session, current.id)


@router.post("/{session_id}/finish", response_model=SessionOut)
async def finish_session(
    session_id: str,
    body: FinishSessionRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Sessiyani yakunlash (izoh + ixtiyoriy baho).

    Ikkala tomon tasdiqlasa status='finished' bo'ladi va coin/XP beriladi.
    """
    service = SessionService(db)
    session = await service.submit_finish(session_id, current.id, body.comment, body.rating)
    if session is None:
        raise HTTPException(status_code=404, detail="Faol sessiya topilmadi")
    return await _session_to_out(db, session, current.id)
