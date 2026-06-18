"""
Reklam alanları (banner/video). Belirli bölgelerde (akış, keşfet, kenarlar)
gösterilir. "Reklam" etiketiyle işaretlenir (frontend).
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.admin import AdSlot, AdSlotPosition
from app.api.deps import get_admin_user

router = APIRouter(prefix="/ads", tags=["Ads"])


def _dict(a: AdSlot) -> dict:
    return {
        "id": str(a.id),
        "name": a.name,
        "position": a.position.value if hasattr(a.position, "value") else a.position,
        "content_html": a.content_html,
        "image_url": a.image_url,
        "link_url": a.link_url,
        "is_active": a.is_active,
        "priority": a.priority,
        "impressions": a.impressions,
        "clicks": a.clicks,
    }


@router.get("")
async def list_active_ads(
    position: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Belirli bir bölge için aktif reklamları döndürür (herkese açık)."""
    now = datetime.utcnow()
    query = (
        select(AdSlot)
        .where(
            and_(
                AdSlot.position == position,
                AdSlot.is_active == True,
                or_(AdSlot.starts_at.is_(None), AdSlot.starts_at <= now),
                or_(AdSlot.expires_at.is_(None), AdSlot.expires_at > now),
            )
        )
        .order_by(AdSlot.priority.desc())
    )
    rows = (await db.execute(query)).scalars().all()
    return {"items": [_dict(a) for a in rows]}


@router.post("/{ad_id}/click")
async def click_ad(ad_id: UUID, db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(AdSlot).where(AdSlot.id == ad_id))).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Reklam bulunamadı")
    ad.clicks = (ad.clicks or 0) + 1
    await db.commit()
    return {"url": ad.link_url}


# ---- Admin yönetimi ----

class AdCreate(BaseModel):
    name: str = Field(..., max_length=100)
    position: AdSlotPosition
    content_html: str = ""
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@router.get("/all")
async def all_ads(admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(AdSlot).order_by(AdSlot.created_at.desc()))).scalars().all()
    return {"items": [_dict(a) for a in rows]}


@router.post("")
async def create_ad(data: AdCreate, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    ad = AdSlot(
        name=data.name,
        position=data.position,
        content_html=data.content_html or "",
        image_url=data.image_url,
        link_url=data.link_url,
        is_active=data.is_active,
        priority=data.priority,
        starts_at=data.starts_at,
        expires_at=data.expires_at,
    )
    db.add(ad)
    await db.commit()
    await db.refresh(ad)
    return _dict(ad)


@router.put("/{ad_id}")
async def update_ad(ad_id: UUID, data: AdCreate, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(AdSlot).where(AdSlot.id == ad_id))).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Reklam bulunamadı")
    for f, v in data.model_dump().items():
        setattr(ad, f, v)
    await db.commit()
    await db.refresh(ad)
    return _dict(ad)


@router.delete("/{ad_id}")
async def delete_ad(ad_id: UUID, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(AdSlot).where(AdSlot.id == ad_id))).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Reklam bulunamadı")
    await db.delete(ad)
    await db.commit()
    return {"ok": True}
