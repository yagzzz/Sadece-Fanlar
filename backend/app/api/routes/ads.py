"""
Özel reklam sistemi (Google Ads değil — platforma özel).

Genel uçlar:
- GET /ads?placement=feed&audience=guest  -> o yerleşim için gösterilecek reklam(lar)
- GET /ads/preroll                         -> bedava video öncesi pre-roll reklam
- POST /ads/{id}/impression                -> izlenim say
- POST /ads/{id}/click                     -> tık say, hedef URL döndür

Admin:
- GET/POST/PUT/DELETE /ads/manage ...
Hedefleme: display_percent (0-100) ile her istekte olasılıksal gösterim;
target_audience ile kitle kısıtı. Böylece "kaç kişinin yüzde kaçına çıkacak"
mantığı sağlanır (normal reklam ağları gibi).
"""
import random
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.advertisement import Advertisement, AdType
from app.api.deps import get_admin_user, get_current_user_optional

router = APIRouter(prefix="/ads", tags=["Ads"])


def _dict(a: Advertisement) -> dict:
    return {
        "id": str(a.id),
        "title": a.title,
        "ad_type": a.ad_type.value if hasattr(a.ad_type, "value") else a.ad_type,
        "placement": a.placement,
        "media_url": a.media_url,
        "text_content": a.text_content,
        "link_url": a.link_url,
        "display_percent": a.display_percent,
        "target_audience": a.target_audience,
        "skip_after": a.skip_after,
        "priority": a.priority,
        "is_active": a.is_active,
        "impressions": a.impressions,
        "clicks": a.clicks,
        "starts_at": a.starts_at.isoformat() if a.starts_at else None,
        "expires_at": a.expires_at.isoformat() if a.expires_at else None,
    }


def _audience_of(user: Optional[User]) -> str:
    if not user:
        return "guests"
    if getattr(user, "is_creator", False):
        return "creators"
    return "subscribers"  # giriş yapmış normal kullanıcı


async def _eligible(db: AsyncSession, placement: str, audience: str) -> List[Advertisement]:
    now = datetime.utcnow()
    rows = (
        await db.execute(
            select(Advertisement)
            .where(
                and_(
                    Advertisement.placement == placement,
                    Advertisement.is_active == True,
                    or_(Advertisement.starts_at.is_(None), Advertisement.starts_at <= now),
                    or_(Advertisement.expires_at.is_(None), Advertisement.expires_at > now),
                    Advertisement.target_audience.in_(["all", audience]),
                )
            )
            .order_by(Advertisement.priority.desc())
        )
    ).scalars().all()
    # display_percent ile olasılıksal filtre (her reklam kendi yüzdesinde gösterilir)
    return [a for a in rows if random.randint(1, 100) <= max(1, min(100, a.display_percent or 100))]


@router.get("")
async def list_active_ads(
    placement: str = Query("feed"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Bir yerleşim için gösterilecek reklamları döndürür ve izlenim sayar."""
    audience = _audience_of(current_user)
    ads = await _eligible(db, placement, audience)
    for a in ads:
        a.impressions = (a.impressions or 0) + 1
    if ads:
        await db.commit()
    return {"items": [_dict(a) for a in ads]}


@router.get("/preroll")
async def get_preroll(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Bedava video öncesi gösterilecek tek bir pre-roll video reklamı."""
    audience = _audience_of(current_user)
    ads = await _eligible(db, "preroll", audience)
    ads = [a for a in ads if a.ad_type == AdType.VIDEO and a.media_url]
    if not ads:
        return {"ad": None}
    ad = ads[0]
    ad.impressions = (ad.impressions or 0) + 1
    await db.commit()
    return {"ad": _dict(ad)}


@router.post("/{ad_id}/impression")
async def impression(ad_id: UUID, db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(Advertisement).where(Advertisement.id == ad_id))).scalar_one_or_none()
    if ad:
        ad.impressions = (ad.impressions or 0) + 1
        await db.commit()
    return {"ok": True}


@router.post("/{ad_id}/click")
async def click_ad(ad_id: UUID, db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(Advertisement).where(Advertisement.id == ad_id))).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Reklam bulunamadı")
    ad.clicks = (ad.clicks or 0) + 1
    await db.commit()
    return {"url": ad.link_url}


# ---- Admin yönetimi ----

class AdCreate(BaseModel):
    title: str = Field(..., max_length=200)
    ad_type: AdType = AdType.IMAGE
    placement: str = Field("feed", max_length=30)
    media_url: Optional[str] = None
    text_content: Optional[str] = None
    link_url: Optional[str] = None
    display_percent: int = Field(100, ge=1, le=100)
    target_audience: str = Field("all", max_length=20)
    skip_after: int = Field(3, ge=0, le=30)
    priority: int = 0
    is_active: bool = True
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@router.get("/all")
async def all_ads(admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Advertisement).order_by(Advertisement.created_at.desc()))).scalars().all()
    return {"items": [_dict(a) for a in rows]}


@router.post("")
async def create_ad(data: AdCreate, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    ad = Advertisement(**data.model_dump())
    db.add(ad)
    await db.commit()
    await db.refresh(ad)
    return _dict(ad)


@router.put("/{ad_id}")
async def update_ad(ad_id: UUID, data: AdCreate, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(Advertisement).where(Advertisement.id == ad_id))).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Reklam bulunamadı")
    for f, v in data.model_dump().items():
        setattr(ad, f, v)
    await db.commit()
    await db.refresh(ad)
    return _dict(ad)


@router.delete("/{ad_id}")
async def delete_ad(ad_id: UUID, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    ad = (await db.execute(select(Advertisement).where(Advertisement.id == ad_id))).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Reklam bulunamadı")
    await db.delete(ad)
    await db.commit()
    return {"ok": True}
