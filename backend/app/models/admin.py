"""
Admin related models - Settings, Pages, Ads, Reports
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SlugMixin

if TYPE_CHECKING:
    from app.models.user import User


class Setting(Base):
    """Site settings"""
    __tablename__ = "settings"
    
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(20), default="string")  # string, number, boolean, json
    group: Mapped[str] = mapped_column(String(50), default="general")
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    __table_args__ = (
        Index('idx_settings_key', key),
        Index('idx_settings_group', group),
    )


# Alias for backwards compatibility
SiteSettings = Setting


class AdminAction(str, Enum):
    """Admin işlem türleri"""
    USER_BAN = "user_ban"
    USER_UNBAN = "user_unban"
    USER_SUSPEND = "user_suspend"
    USER_VERIFY = "user_verify"
    USER_REJECT_VERIFICATION = "user_reject_verification"
    POST_APPROVE = "post_approve"
    POST_REJECT = "post_reject"
    POST_DELETE = "post_delete"
    POST_PIN = "post_pin"
    POST_UNPIN = "post_unpin"
    COMMENT_DELETE = "comment_delete"
    MESSAGE_DELETE = "message_delete"
    USER_DELETE = "user_delete"
    USER_PROMOTE = "user_promote"
    USER_DEMOTE = "user_demote"
    REPORT_RESOLVE = "report_resolve"
    REPORT_DISMISS = "report_dismiss"
    SETTINGS_CHANGE = "settings_change"
    WITHDRAWAL_APPROVE = "withdrawal_approve"
    WITHDRAWAL_REJECT = "withdrawal_reject"
    WITHDRAWAL_PROCESS = "withdrawal_process"
    PAYMENT_REFUND = "payment_refund"


class AdminLog(Base):
    """Admin işlem kayıtları"""
    __tablename__ = "admin_logs"
    
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # İşlem bilgileri
    action: Mapped[AdminAction] = mapped_column(SQLEnum(AdminAction), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Hedef (varsa)
    target_type: Mapped[Optional[str]] = mapped_column(String(50))  # user, post, report, etc.
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Ek veriler
    data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # IP adresi
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    # İlişkiler
    admin: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_admin_logs_admin_id', admin_id),
        Index('idx_admin_logs_action', action),
        Index('idx_admin_logs_created_at', 'created_at'),
    )


class Announcement(Base):
    """Site duyuruları"""
    __tablename__ = "announcements"
    
    # Duyuru içeriği
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str] = mapped_column(Text)
    
    # Görünürlük
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Zamanlama
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Hedef kitle
    target_users: Mapped[str] = mapped_column(String(20), default="all")  # all, creators, subscribers
    
    # Oluşturan
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # İlişkiler
    created_by: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_announcements_active', is_active),
        Index('idx_announcements_pinned', is_pinned),
    )


class PublicPage(Base, SlugMixin):
    """Static pages (Terms, Privacy, etc.)"""
    __tablename__ = "public_pages"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    
    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_public_pages_slug', 'slug'),
    )


class AdSlotPosition(str, Enum):
    HEADER = "header"
    SIDEBAR = "sidebar"
    FEED = "feed"
    FOOTER = "footer"
    PROFILE = "profile"
    POST = "post"


class AdSlot(Base):
    """Advertisement slots"""
    __tablename__ = "ad_slots"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[AdSlotPosition] = mapped_column(SQLEnum(AdSlotPosition), nullable=False)
    
    # Content
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    link_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Targeting
    target_countries: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Schedule
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Stats
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    
    # Priority (higher = shown first)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_ad_slots_position', position),
        Index('idx_ad_slots_active', is_active),
    )


class FeaturedUser(Base):
    """Featured creators on homepage"""
    __tablename__ = "featured_users"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Display
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Schedule
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_featured_users_active', is_active),
        Index('idx_featured_users_sort', sort_order),
    )


class ReportType(str, Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    ILLEGAL_CONTENT = "illegal_content"
    UNDERAGE = "underage"
    IMPERSONATION = "impersonation"
    COPYRIGHT = "copyright"
    OTHER = "other"


class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Report(Base):
    """User reports"""
    __tablename__ = "reports"
    
    reporter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # What's being reported
    reported_type: Mapped[str] = mapped_column(String(50), nullable=False)  # user, post, message, comment
    reported_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reported_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Report details
    type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Evidence
    screenshot_urls: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Status
    status: Mapped[ReportStatus] = mapped_column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    
    # Resolution
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_note: Mapped[Optional[str]] = mapped_column(Text)
    action_taken: Mapped[Optional[str]] = mapped_column(String(100))  # warning, suspension, ban, none
    
    # Relationships
    reporter: Mapped["User"] = relationship("User", foreign_keys=[reporter_id])
    reported_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reported_user_id])
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by_id])
    
    __table_args__ = (
        Index('idx_reports_status', status),
        Index('idx_reports_type', type),
        Index('idx_reports_reported_user', reported_user_id),
    )


class ContactMessage(Base):
    """Contact form submissions"""
    __tablename__ = "contact_messages"
    
    # Sender info (can be anonymous)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Message
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_replied: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Reply
    replied_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reply_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_contact_messages_is_read', is_read),
    )


class ReferralCodeUsage(Base):
    """Track referral code usage"""
    __tablename__ = "referral_code_usages"
    
    referrer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    referred_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    referral_code: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Bonus tracking
    referrer_bonus: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    referred_bonus: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    bonus_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    referrer: Mapped["User"] = relationship("User", foreign_keys=[referrer_id])
    referred: Mapped["User"] = relationship("User", foreign_keys=[referred_id])
    
    __table_args__ = (
        Index('idx_referral_usages_referrer', referrer_id),
        Index('idx_referral_usages_referred', referred_id, unique=True),
    )
