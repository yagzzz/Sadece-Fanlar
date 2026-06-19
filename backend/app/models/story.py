"""
Şipşak (tek görüntülük / 24 saatlik hikaye) modelleri.

- Story: içerik üreticisinin yüklediği kısa ömürlü medya. 24 saat sonra
  (expires_at) görünmez. `is_single_view=True` ise her izleyici yalnızca
  BİR KEZ açabilir (Snapchat tarzı "şipşak").
- StoryView: hangi izleyicinin hangi hikayeyi gördüğünü tutar; tek görüntülük
  içerikte tekrar açmayı engeller ve görüntülenme sayısını sağlar.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Integer, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class StoryMediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class Story(Base):
    __tablename__ = "stories"

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    media_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    media_type: Mapped[StoryMediaType] = mapped_column(
        SQLEnum(StoryMediaType), default=StoryMediaType.IMAGE
    )
    caption: Mapped[Optional[str]] = mapped_column(String(500))

    # Tek görüntülük "şipşak": her izleyici yalnızca bir kez açabilir.
    is_single_view: Mapped[bool] = mapped_column(Boolean, default=False)
    # Aboneye özel mi? (False ise herkese açık önizleme)
    subscribers_only: Mapped[bool] = mapped_column(Boolean, default=False)

    view_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])

    __table_args__ = (
        Index("idx_stories_creator_id", "creator_id"),
        Index("idx_stories_expires_at", "expires_at"),
    )


class StoryView(Base):
    __tablename__ = "story_views"

    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    viewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("story_id", "viewer_id", name="uq_story_view"),
        Index("idx_story_views_story", "story_id"),
        Index("idx_story_views_viewer", "viewer_id"),
    )
