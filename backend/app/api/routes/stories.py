"""
Şipşak / Hikaye (Stories) API.

- Üreticiler 24 saatlik (varsayılan) medya paylaşır.
- `single_view=True` ise her izleyici içeriği yalnızca BİR KEZ açabilir.
- `subscribers_only=True` ise yalnızca aktif aboneler görebilir.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID


def _utcnow() -> datetime:
    """Timezone-aware UTC now (DB timestamptz ile güvenli karşılaştırma için)."""
    return datetime.now(timezone.utc)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.story import Story, StoryView, StoryMediaType
from app.models.subscription import Subscription, SubscriptionStatus
from app.api.deps import get_current_user

router = APIRouter(prefix="/stories", tags=["Stories"])


class StoryCreate(BaseModel):
    media_url: str = Field(..., min_length=4, max_length=1000)
    media_type: StoryMediaType = StoryMediaType.IMAGE
    caption: Optional[str] = Field(None, max_length=500)
    single_view: bool = False
    subscribers_only: bool = False
    duration_hours: int = Field(24, ge=1, le=72)


def _story_dict(s: Story, creator: User, viewed: bool = False) -> dict:
    return {
        "id": str(s.id),
        "creator_id": str(s.creator_id),
        "creator_username": creator.username if creator else None,
        "creator_display_name": (creator.display_name or creator.username) if creator else None,
        "creator_avatar": creator.avatar_url if creator else None,
        "media_type": s.media_type.value if hasattr(s.media_type, "value") else s.media_type,
        "caption": s.caption,
        "is_single_view": s.is_single_view,
        "subscribers_only": s.subscribers_only,
        "view_count": s.view_count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "expires_at": s.expires_at.isoformat() if s.expires_at else None,
        "viewed": viewed,
    }


async def _has_active_sub(db: AsyncSession, subscriber_id: UUID, creator_id: UUID) -> bool:
    row = await db.execute(
        select(Subscription.id).where(
            and_(
                Subscription.subscriber_id == subscriber_id,
                Subscription.creator_id == creator_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.expires_at > _utcnow(),
            )
        ).limit(1)
    )
    return row.scalar_one_or_none() is not None


@router.post("")
async def create_story(
    data: StoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Hikaye oluştur (yalnızca içerik üreticileri)."""
    if not getattr(current_user, "is_creator", False):
        raise HTTPException(status_code=403, detail="Yalnızca içerik üreticileri hikaye paylaşabilir")

    story = Story(
        creator_id=current_user.id,
        media_url=data.media_url,
        media_type=data.media_type,
        caption=data.caption,
        is_single_view=data.single_view,
        subscribers_only=data.subscribers_only,
        expires_at=_utcnow() + timedelta(hours=data.duration_hours),
    )
    db.add(story)
    await db.commit()
    await db.refresh(story)
    return _story_dict(story, current_user, viewed=False)


@router.get("")
async def list_stories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Aktif (süresi dolmamış) hikayeleri üreticiye göre gruplar.
    Tek görüntülük + izlenmiş hikayeler 'viewed=true' işaretlenir (önizlemede gri halka).
    """
    now = _utcnow()
    rows = (
        await db.execute(
            select(Story, User)
            .join(User, User.id == Story.creator_id)
            .where(Story.expires_at > now)
            .order_by(Story.created_at.desc())
        )
    ).all()

    # İzleyicinin gördüğü hikaye id'leri
    viewed_ids = set()
    if rows:
        seen = await db.execute(
            select(StoryView.story_id).where(StoryView.viewer_id == current_user.id)
        )
        viewed_ids = {r for (r,) in seen.all()}

    groups: dict[str, dict] = {}
    for s, creator in rows:
        # Aboneye özel ve abone değilse + sahibi değilse atla
        if s.subscribers_only and creator.id != current_user.id:
            if not await _has_active_sub(db, current_user.id, creator.id):
                continue
        key = str(creator.id)
        if key not in groups:
            groups[key] = {
                "creator_id": key,
                "creator_username": creator.username,
                "creator_display_name": creator.display_name or creator.username,
                "creator_avatar": creator.avatar_url,
                "stories": [],
                "all_viewed": True,
            }
        viewed = s.id in viewed_ids
        if not viewed:
            groups[key]["all_viewed"] = False
        groups[key]["stories"].append(_story_dict(s, creator, viewed=viewed))

    return {"items": list(groups.values())}


@router.post("/{story_id}/view")
async def view_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Hikayeyi aç. Tek görüntülük içerik daha önce açıldıysa medya döndürülmez.
    """
    s = (await db.execute(select(Story).where(Story.id == story_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Hikaye bulunamadı")
    if s.expires_at <= _utcnow():
        raise HTTPException(status_code=410, detail="Hikayenin süresi dolmuş")

    creator = (await db.execute(select(User).where(User.id == s.creator_id))).scalar_one_or_none()
    is_owner = s.creator_id == current_user.id

    # Aboneye özel erişim kontrolü
    if s.subscribers_only and not is_owner:
        if not await _has_active_sub(db, current_user.id, s.creator_id):
            raise HTTPException(status_code=403, detail="Bu hikaye yalnızca abonelere açık")

    # Daha önce görülmüş mü?
    existing = (
        await db.execute(
            select(StoryView).where(
                and_(StoryView.story_id == story_id, StoryView.viewer_id == current_user.id)
            )
        )
    ).scalar_one_or_none()

    already_viewed = existing is not None

    # Tek görüntülük: sahibi değilse ve daha önce görmüşse medyayı verme
    if s.is_single_view and not is_owner and already_viewed:
        return {
            **_story_dict(s, creator, viewed=True),
            "media_url": None,
            "consumed": True,
        }

    # İlk görüntüleme: kaydet + sayaç artır (sahibi kendi görüntülemesini saymaz)
    if not already_viewed and not is_owner:
        db.add(StoryView(story_id=story_id, viewer_id=current_user.id))
        s.view_count = (s.view_count or 0) + 1
        await db.commit()

    return {
        **_story_dict(s, creator, viewed=True),
        "media_url": s.media_url,
        "consumed": s.is_single_view and not is_owner,
    }


@router.delete("/{story_id}")
async def delete_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Üretici kendi hikayesini siler."""
    s = (await db.execute(select(Story).where(Story.id == story_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Hikaye bulunamadı")
    if s.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu hikaye size ait değil")
    await db.execute(delete(StoryView).where(StoryView.story_id == story_id))
    await db.delete(s)
    await db.commit()
    return {"success": True, "message": "Hikaye silindi"}
