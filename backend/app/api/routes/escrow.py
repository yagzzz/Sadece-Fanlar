"""
Escrow (emanetli özel istek) sistemi.

Akış:
1. Fan istek oluşturur ve parayı yatırır -> para emanette (pending_balance) bekler.
2. Üretici teslim eder (DELIVERED).
3. Fan onaylar -> para (komisyonlu) üreticiye geçer (COMPLETED).
4. Anlaşmazlık olursa yönetici karar verir (iade veya serbest bırakma).
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.support import EscrowRequest, EscrowStatus
from app.models.transaction import TransactionType
from app.api.deps import get_current_user, get_staff_user
from app.services import wallet_service
from app.services.site_settings import get_fee_percent

router = APIRouter(prefix="/escrow", tags=["Escrow"])


class EscrowCreate(BaseModel):
    creator_username: str
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=1, max_length=4000)
    amount: float = Field(..., gt=0)


class DeliverData(BaseModel):
    note: str = Field("", max_length=2000)
    url: Optional[str] = None


class DisputeData(BaseModel):
    reason: str = Field(..., min_length=1, max_length=2000)


def _dict(e: EscrowRequest) -> dict:
    return {
        "id": str(e.id),
        "buyer_id": str(e.buyer_id),
        "creator_id": str(e.creator_id),
        "title": e.title,
        "description": e.description,
        "amount": float(e.amount),
        "status": e.status.value if hasattr(e.status, "value") else e.status,
        "delivery_note": e.delivery_note,
        "delivery_url": e.delivery_url,
        "dispute_reason": e.dispute_reason,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


@router.post("")
async def create_escrow(
    data: EscrowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Özel istek oluştur ve parayı emanete yatır."""
    creator = (
        await db.execute(select(User).where(User.username == data.creator_username.lower()))
    ).scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="İçerik üreticisi bulunamadı")
    if creator.id == current_user.id:
        raise HTTPException(status_code=400, detail="Kendinize istek oluşturamazsınız")

    try:
        await wallet_service.hold(db, current_user.id, data.amount)
    except ValueError:
        raise HTTPException(status_code=400, detail="Yetersiz bakiye")

    escrow = EscrowRequest(
        buyer_id=current_user.id,
        creator_id=creator.id,
        title=data.title,
        description=data.description,
        amount=round(data.amount, 2),
        status=EscrowStatus.FUNDED,
        funded_at=datetime.utcnow(),
    )
    db.add(escrow)
    await db.commit()
    await db.refresh(escrow)
    return _dict(escrow)


@router.get("")
async def my_escrows(
    role: str = Query("all", description="all | buyer | creator"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(EscrowRequest)
    if role == "buyer":
        query = query.where(EscrowRequest.buyer_id == current_user.id)
    elif role == "creator":
        query = query.where(EscrowRequest.creator_id == current_user.id)
    else:
        query = query.where(
            or_(EscrowRequest.buyer_id == current_user.id, EscrowRequest.creator_id == current_user.id)
        )
    rows = (await db.execute(query.order_by(EscrowRequest.created_at.desc()))).scalars().all()
    return {"items": [_dict(e) for e in rows]}


@router.get("/disputes")
async def list_disputes(
    staff: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Yönetici/moderatör: anlaşmazlıktaki tüm emanet isteklerini listeler."""
    rows = (
        await db.execute(
            select(EscrowRequest)
            .where(EscrowRequest.status == EscrowStatus.DISPUTED)
            .order_by(EscrowRequest.created_at.desc())
        )
    ).scalars().all()
    return {"items": [_dict(e) for e in rows]}


async def _get_owned(db, escrow_id: UUID, user: User) -> EscrowRequest:
    e = (await db.execute(select(EscrowRequest).where(EscrowRequest.id == escrow_id))).scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="İstek bulunamadı")
    if user.id not in (e.buyer_id, e.creator_id):
        raise HTTPException(status_code=403, detail="Bu isteğe erişiminiz yok")
    return e


@router.post("/{escrow_id}/deliver")
async def deliver(
    escrow_id: UUID,
    data: DeliverData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Üretici teslimi işaretler."""
    e = await _get_owned(db, escrow_id, current_user)
    if e.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece üretici teslim edebilir")
    if e.status != EscrowStatus.FUNDED:
        raise HTTPException(status_code=400, detail="İstek teslim edilebilir durumda değil")
    e.status = EscrowStatus.DELIVERED
    e.delivery_note = data.note
    e.delivery_url = data.url
    e.delivered_at = datetime.utcnow()
    await db.commit()
    return _dict(e)


@router.post("/{escrow_id}/approve")
async def approve(
    escrow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fan teslimi onaylar -> para üreticiye (komisyonlu) geçer."""
    e = await _get_owned(db, escrow_id, current_user)
    if e.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece alıcı onaylayabilir")
    if e.status != EscrowStatus.DELIVERED:
        raise HTTPException(status_code=400, detail="Önce teslim edilmeli")

    fee = await get_fee_percent(db)
    await wallet_service.release_hold(
        db, e.buyer_id, e.creator_id, float(e.amount), fee,
        TransactionType.MESSAGE, description=f"Özel istek: {e.title}", commit=False,
    )
    e.status = EscrowStatus.COMPLETED
    e.completed_at = datetime.utcnow()
    await db.commit()
    return _dict(e)


@router.post("/{escrow_id}/cancel")
async def cancel(
    escrow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Teslim edilmeden iptal: para fan'a iade."""
    e = await _get_owned(db, escrow_id, current_user)
    if e.status not in (EscrowStatus.FUNDED,):
        raise HTTPException(status_code=400, detail="Bu aşamada iptal edilemez")
    # Alıcı her zaman, üretici de isteği reddetmek için iptal edebilir
    await wallet_service.refund_hold(db, e.buyer_id, float(e.amount), commit=False)
    e.status = EscrowStatus.REFUNDED
    await db.commit()
    return _dict(e)


@router.post("/{escrow_id}/dispute")
async def dispute(
    escrow_id: UUID,
    data: DisputeData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Anlaşmazlık aç (yönetici karar verecek)."""
    e = await _get_owned(db, escrow_id, current_user)
    if e.status not in (EscrowStatus.FUNDED, EscrowStatus.DELIVERED):
        raise HTTPException(status_code=400, detail="Bu aşamada anlaşmazlık açılamaz")
    e.status = EscrowStatus.DISPUTED
    e.dispute_reason = data.reason
    await db.commit()
    return _dict(e)


@router.post("/{escrow_id}/resolve")
async def resolve_dispute(
    escrow_id: UUID,
    action: str = Query(..., description="release | refund"),
    staff: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Yönetici/moderatör anlaşmazlığı çözer."""
    e = (await db.execute(select(EscrowRequest).where(EscrowRequest.id == escrow_id))).scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="İstek bulunamadı")
    if e.status != EscrowStatus.DISPUTED:
        raise HTTPException(status_code=400, detail="İstek anlaşmazlıkta değil")

    if action == "release":
        fee = await get_fee_percent(db)
        await wallet_service.release_hold(
            db, e.buyer_id, e.creator_id, float(e.amount), fee,
            TransactionType.MESSAGE, description=f"Özel istek (yönetici onayı): {e.title}", commit=False,
        )
        e.status = EscrowStatus.COMPLETED
        e.completed_at = datetime.utcnow()
    elif action == "refund":
        await wallet_service.refund_hold(db, e.buyer_id, float(e.amount), commit=False)
        e.status = EscrowStatus.REFUNDED
    else:
        raise HTTPException(status_code=400, detail="action: release veya refund")

    await db.commit()
    return _dict(e)
