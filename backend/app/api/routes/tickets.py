"""
Destek talebi (ticket) sistemi.
Talep oluşturulur; yetkili yanıtlayınca canlı sohbet akışına dönüşür.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.support import SupportTicket, TicketMessage, TicketStatus, TicketCategory
from app.api.deps import get_current_user, get_staff_user

router = APIRouter(prefix="/tickets", tags=["Support"])


class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=3, max_length=200)
    category: TicketCategory = TicketCategory.GENERAL
    message: str = Field(..., min_length=1, max_length=4000)


class TicketReply(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)


def _ticket_dict(t: SupportTicket, include_messages: bool = False) -> dict:
    d = {
        "id": str(t.id),
        "subject": t.subject,
        "category": t.category.value if hasattr(t.category, "value") else t.category,
        "status": t.status.value if hasattr(t.status, "value") else t.status,
        "user_id": str(t.user_id),
        "last_message_at": t.last_message_at.isoformat() if t.last_message_at else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }
    if include_messages:
        d["messages"] = [
            {
                "id": str(m.id),
                "sender_id": str(m.sender_id),
                "is_staff": m.is_staff,
                "text": m.text,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in sorted(t.messages, key=lambda x: x.created_at or datetime.min)
        ]
    return d


@router.post("")
async def create_ticket(
    data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=data.subject,
        category=data.category,
        status=TicketStatus.OPEN,
        last_message_at=datetime.utcnow(),
    )
    db.add(ticket)
    await db.flush()
    db.add(TicketMessage(ticket_id=ticket.id, sender_id=current_user.id, is_staff=False, text=data.message))
    await db.commit()
    await db.refresh(ticket)
    return _ticket_dict(ticket)


@router.get("")
async def my_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(SupportTicket)
            .where(SupportTicket.user_id == current_user.id)
            .order_by(SupportTicket.last_message_at.desc())
        )
    ).scalars().all()
    return {"items": [_ticket_dict(t) for t in rows]}


@router.get("/queue")
async def ticket_queue(
    status_filter: Optional[TicketStatus] = Query(None),
    staff: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SupportTicket)
    if status_filter:
        query = query.where(SupportTicket.status == status_filter)
    else:
        query = query.where(SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.ANSWERED]))
    rows = (await db.execute(query.order_by(SupportTicket.last_message_at.desc()))).scalars().all()
    return {"items": [_ticket_dict(t) for t in rows]}


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = (
        await db.execute(
            select(SupportTicket)
            .options(selectinload(SupportTicket.messages))
            .where(SupportTicket.id == ticket_id)
        )
    ).scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")

    is_staff = current_user.role in ("admin", "moderator") or str(getattr(current_user.role, "value", current_user.role)) in ("admin", "moderator")
    if ticket.user_id != current_user.id and not is_staff:
        raise HTTPException(status_code=403, detail="Bu talebe erişiminiz yok")

    return _ticket_dict(ticket, include_messages=True)


@router.post("/{ticket_id}/reply")
async def reply_ticket(
    ticket_id: UUID,
    data: TicketReply,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = (await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))).scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")

    role = str(getattr(current_user.role, "value", current_user.role))
    is_staff = role in ("admin", "moderator")
    if ticket.user_id != current_user.id and not is_staff:
        raise HTTPException(status_code=403, detail="Bu talebe erişiminiz yok")
    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Bu talep kapatılmış")

    db.add(TicketMessage(ticket_id=ticket.id, sender_id=current_user.id, is_staff=is_staff, text=data.text))
    ticket.last_message_at = datetime.utcnow()
    if is_staff:
        ticket.status = TicketStatus.ANSWERED
        if not ticket.assigned_to_id:
            ticket.assigned_to_id = current_user.id
    await db.commit()
    return {"ok": True}


@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = (await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))).scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")
    role = str(getattr(current_user.role, "value", current_user.role))
    if ticket.user_id != current_user.id and role not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Yetki yok")
    ticket.status = TicketStatus.CLOSED
    await db.commit()
    return {"ok": True}
