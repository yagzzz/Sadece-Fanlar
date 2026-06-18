"""
Kullanıcı Modelleri - User Models
================================
Bu dosya kullanıcılarla ilgili tüm veritabanı modellerini içerir:
- User: Ana kullanıcı modeli (üreticiler ve aboneler)
- UserVerification: Kimlik doğrulama bilgileri
- UserSettings: Kullanıcı ayarları
- UserDevice: Cihaz bilgileri (bildirimler için)
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.subscription import Subscription
    from app.models.transaction import Wallet, Transaction, Withdrawal
    from app.models.message import Conversation
    from app.models.notification import Notification
    from app.models.stream import Stream


class UserRole(str, Enum):
    """
    Kullanıcı rolleri - User roles
    ADMIN: Sistem yöneticisi
    CREATOR: İçerik üreticisi
    USER: Normal kullanıcı
    """
    ADMIN = "admin"
    MODERATOR = "moderator"
    CREATOR = "creator"
    USER = "user"


class UserStatus(str, Enum):
    """
    Kullanıcı hesap durumları - User account statuses
    """
    ACTIVE = "active"        # Aktif hesap
    SUSPENDED = "suspended"  # Askıya alınmış
    BANNED = "banned"        # Yasaklanmış
    DELETED = "deleted"      # Silinmiş


class VerificationStatus(str, Enum):
    """
    Doğrulama durumları - Verification statuses
    PENDING: Beklemede
    APPROVED: Onaylandı
    REJECTED: Reddedildi
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base, SoftDeleteMixin):
    """
    Ana kullanıcı modeli - Main user model
    Hem içerik üreticileri hem de aboneler için kullanılır
    """
    __tablename__ = "users"
    
    # Kimlik doğrulama alanları - Authentication fields
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    # E-posta ANONİMLİK için opsiyoneldir. Yalnızca kullanıcı isterse (parola
    # kurtarma vb.) verilir. PostgreSQL'de unique index birden fazla NULL'a izin verir.
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Profile fields
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    cover_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Creator settings
    is_creator: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified_creator: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0)
    subscription_price_3m: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    subscription_price_6m: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    subscription_price_12m: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    is_free_profile: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Security
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255))

    # Moderasyon - Moderation
    banned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ban_reason: Mapped[Optional[str]] = mapped_column(Text)

    # İçerik üreticisinin yaş beyanı (18+) - yasal asgari, kimlik bilgisi toplanmaz
    age_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Privacy
    is_public_profile: Mapped[bool] = mapped_column(Boolean, default=False)
    show_subscribers_count: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_comments: Mapped[bool] = mapped_column(Boolean, default=True)
    geo_block_countries: Mapped[Optional[list]] = mapped_column(ARRAY(String), default=[])

    # Mesajlaşma ayarları - kimler mesaj gönderebilir / ücretli mesaj fiyatı
    # "everyone" | "subscribers" | "paid"
    messages_restriction: Mapped[str] = mapped_column(String(20), default="everyone")
    message_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # Referral
    referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    referred_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Stats (denormalized for performance)
    posts_count: Mapped[int] = mapped_column(Integer, default=0)
    subscribers_count: Mapped[int] = mapped_column(Integer, default=0)
    subscriptions_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="author", lazy="dynamic")
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="user", uselist=False)
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", 
        foreign_keys="Subscription.subscriber_id",
        back_populates="subscriber",
        lazy="dynamic"
    )
    subscribers: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        foreign_keys="Subscription.creator_id",
        back_populates="creator",
        lazy="dynamic"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id",
        lazy="dynamic",
    )
    streams: Mapped[List["Stream"]] = relationship("Stream", back_populates="creator", lazy="dynamic")
    verification: Mapped[Optional["UserVerification"]] = relationship(
        "UserVerification",
        back_populates="user",
        foreign_keys="UserVerification.user_id",
        uselist=False,
    )
    settings: Mapped[Optional["UserSettings"]] = relationship("UserSettings", back_populates="user", uselist=False)
    devices: Mapped[List["UserDevice"]] = relationship("UserDevice", back_populates="user", lazy="dynamic")
    
    # Veritabanı indexleri - Database indexes for faster queries
    __table_args__ = (
        Index('idx_users_username_lower', 'username'),  # Kullanıcı adı aramaları için
        Index('idx_users_is_creator', 'is_creator'),    # İçerik üreticileri filtrelemek için
        Index('idx_users_created_at', 'created_at'),    # Tarih sıralaması için
    )
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserVerification(Base):
    """Creator verification documents"""
    __tablename__ = "user_verifications"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus), 
        default=VerificationStatus.PENDING
    )
    
    # Documents
    id_document_url: Mapped[Optional[str]] = mapped_column(String(500))
    id_document_type: Mapped[Optional[str]] = mapped_column(String(50))  # passport, id_card, drivers_license
    selfie_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Verification details
    legal_name: Mapped[Optional[str]] = mapped_column(String(255))
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    address: Mapped[Optional[str]] = mapped_column(Text)
    country: Mapped[Optional[str]] = mapped_column(String(2))  # ISO 3166-1 alpha-2
    
    # Admin fields
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="verification", foreign_keys=[user_id])


class UserSettings(Base):
    """User preferences and settings"""
    __tablename__ = "user_settings"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_subscriber: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_tip: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_message: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_comment: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Display preferences
    theme: Mapped[str] = mapped_column(String(20), default="system")  # light, dark, system
    language: Mapped[str] = mapped_column(String(10), default="tr")
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Istanbul")
    
    # Privacy preferences
    show_online_status: Mapped[bool] = mapped_column(Boolean, default=True)
    show_last_seen: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_message_requests: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Payment preferences
    default_payment_method: Mapped[Optional[str]] = mapped_column(String(20))  # monero, btcpay
    auto_withdraw: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_withdraw_threshold: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    monero_address: Mapped[Optional[str]] = mapped_column(String(100))
    btc_address: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")


class UserDevice(Base):
    """User devices for 2FA and session management"""
    __tablename__ = "user_devices"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    device_name: Mapped[str] = mapped_column(String(100))
    device_type: Mapped[str] = mapped_column(String(50))  # web, mobile, tablet
    browser: Mapped[Optional[str]] = mapped_column(String(100))
    os: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    # Session
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(String(255))
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="devices")
    
    __table_args__ = (
        Index('idx_user_devices_user_id', user_id),
        Index('idx_user_devices_refresh_token', refresh_token_hash),
    )
