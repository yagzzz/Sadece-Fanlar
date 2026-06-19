"""
Gelişmiş özel reklam modeli (Google Ads değil, platforma özel).

Admin panelden yönetilir:
- ad_type: image | video | text
- placement: feed | explore | explore_left | explore_right | sidebar | preroll
- display_percent: bu reklamın kaç % izlenimde gösterileceği (hedefleme)
- target_audience: all | guests | subscribers | creators
- skip_after: pre-roll videolarda kaç saniye sonra atlanabilir (varsayılan 3)
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Integer, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AdType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"


class Advertisement(Base):
    __tablename__ = "advertisements"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    ad_type: Mapped[AdType] = mapped_column(SQLEnum(AdType), default=AdType.IMAGE)

    # Nerede gösterilecek: feed, explore, explore_left, explore_right, sidebar, preroll
    placement: Mapped[str] = mapped_column(String(30), default="feed")

    media_url: Mapped[Optional[str]] = mapped_column(String(1000))   # resim/video adresi
    text_content: Mapped[Optional[str]] = mapped_column(Text)        # metin reklam içeriği
    link_url: Mapped[Optional[str]] = mapped_column(String(1000))    # tıklanınca gidilecek

    # Hedefleme: bu reklam, uygun izlenimlerin yüzde kaçında gösterilsin (0-100)
    display_percent: Mapped[int] = mapped_column(Integer, default=100)
    # Kitle: all | guests | subscribers | creators
    target_audience: Mapped[str] = mapped_column(String(20), default="all")

    # Pre-roll: kaç saniye sonra atlanabilir
    skip_after: Mapped[int] = mapped_column(Integer, default=3)

    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        Index("idx_ads_placement", "placement"),
        Index("idx_ads_active", "is_active"),
    )
