"""
Bildirim Modeli
===============
Bu dosya kullanıcı bildirimleri ile ilgili veritabanı modellerini içerir.

İçerdiği modeller:
- NotificationType: Bildirim türleri (yeni abone, bahşiş, yorum, vb.)
- Notification: Kullanıcı bildirimleri
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, Enum):
    """Bildirim türü - Bildirimin ne hakkında olduğu"""
    
    # Abonelik bildirimleri
    NEW_SUBSCRIBER = "new_subscriber"           # Yeni abone
    SUBSCRIPTION_EXPIRING = "subscription_expiring"  # Abonelik sona ermek üzere
    SUBSCRIPTION_EXPIRED = "subscription_expired"    # Abonelik sona erdi
    SUBSCRIPTION_RENEWED = "subscription_renewed"    # Abonelik yenilendi
    
    # Para ile ilgili bildirimler
    NEW_TIP = "new_tip"                         # Yeni bahşiş
    NEW_MESSAGE_TIP = "new_message_tip"         # Mesajla gelen bahşiş
    POST_UNLOCKED = "post_unlocked"             # Gönderi kilidi açıldı
    MESSAGE_UNLOCKED = "message_unlocked"       # Mesaj kilidi açıldı
    WITHDRAWAL_APPROVED = "withdrawal_approved"  # Para çekme onaylandı
    WITHDRAWAL_COMPLETED = "withdrawal_completed"  # Para çekme tamamlandı
    WITHDRAWAL_REJECTED = "withdrawal_rejected"  # Para çekme reddedildi
    DEPOSIT_RECEIVED = "deposit_received"       # Para yatırıldı
    
    # Etkileşim bildirimleri
    NEW_LIKE = "new_like"                       # Yeni beğeni
    NEW_COMMENT = "new_comment"                 # Yeni yorum
    NEW_COMMENT_REPLY = "new_comment_reply"     # Yoruma yanıt
    NEW_MENTION = "new_mention"                 # Bahsetme
    MENTION = "mention"                         # Kısa alias
    NEW_FOLLOWER = "new_follower"               # Yeni takipçi
    
    # Mesaj bildirimleri
    NEW_MESSAGE = "new_message"                 # Yeni mesaj
    NEW_MESSAGE_REQUEST = "new_message_request"  # Yeni mesaj isteği
    
    # Canlı yayın bildirimleri
    STREAM_STARTED = "stream_started"           # Yayın başladı
    STREAM_REMINDER = "stream_reminder"         # Yayın hatırlatması
    NEW_STREAM = "new_stream"                   # Yeni yayın bildirimi
    
    # Sistem bildirimleri
    VERIFICATION_APPROVED = "verification_approved"  # Doğrulama onaylandı
    VERIFICATION_REJECTED = "verification_rejected"  # Doğrulama reddedildi
    POST_APPROVED = "post_approved"             # Gönderi onaylandı
    POST_REJECTED = "post_rejected"             # Gönderi reddedildi
    ACCOUNT_WARNING = "account_warning"         # Hesap uyarısı
    ANNOUNCEMENT = "announcement"               # Duyuru


class Notification(Base):
    """
    Bildirim Modeli
    ===============
    Kullanıcılara gönderilen bildirimler.
    Yeni aboneler, bahşişler, yorumlar, sistem bildirimleri vb.
    E-posta bildirimi gönderme durumu da takip edilir.
    """
    __tablename__ = "notifications"
    
    # Bildirimin sahibi
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Bildirim türü ve içeriği
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)   # Bildirim başlığı
    message: Mapped[str] = mapped_column(Text, nullable=False)        # Bildirim mesajı
    
    # Bildirimi tetikleyen kullanıcı (varsa)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # İlişkili öğe (polimorfik referans)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50))  # post, message, subscription, vb.
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Yönlendirme linki
    link: Mapped[Optional[str]] = mapped_column(String(500))  # Tıklanınca gidilecek sayfa
    
    # Okunma durumu
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)                      # Okundu mu?
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))       # Okunma zamanı
    
    # E-posta bildirimi
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)  # E-posta gönderildi mi?
    
    # Ek veriler (JSON formatında)
    data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # İlişkiler
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="notifications")  # Bildirim sahibi
    actor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[actor_id])  # Tetikleyen kullanıcı
    
    # Veritabanı indexleri - Sorgu performansı için
    __table_args__ = (
        Index('idx_notifications_user_id', 'user_id'),      # Kullanıcı bildirimleri için
        Index('idx_notifications_is_read', 'is_read'),      # Okunmamış filtrelemesi
        Index('idx_notifications_created_at', 'created_at'), # Tarih sıralaması
        Index('idx_notifications_type', 'type'),            # Tip filtrelemesi
    )


class NotificationSettings(Base):
    """
    Bildirim Ayarları Modeli
    ========================
    Kullanıcının hangi bildirimleri almak istediğini belirler.
    """
    __tablename__ = "notification_settings"
    
    # Ayarların sahibi
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # E-posta bildirimleri
    email_new_subscriber: Mapped[bool] = mapped_column(Boolean, default=True)
    email_new_tip: Mapped[bool] = mapped_column(Boolean, default=True)
    email_new_message: Mapped[bool] = mapped_column(Boolean, default=True)
    email_new_comment: Mapped[bool] = mapped_column(Boolean, default=True)
    email_subscription_expiring: Mapped[bool] = mapped_column(Boolean, default=True)
    email_withdrawal: Mapped[bool] = mapped_column(Boolean, default=True)
    email_announcements: Mapped[bool] = mapped_column(Boolean, default=True)
    email_marketing: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Push bildirimleri
    push_new_subscriber: Mapped[bool] = mapped_column(Boolean, default=True)
    push_new_tip: Mapped[bool] = mapped_column(Boolean, default=True)
    push_new_message: Mapped[bool] = mapped_column(Boolean, default=True)
    push_new_comment: Mapped[bool] = mapped_column(Boolean, default=True)
    push_new_like: Mapped[bool] = mapped_column(Boolean, default=True)
    push_mentions: Mapped[bool] = mapped_column(Boolean, default=True)
    push_stream_started: Mapped[bool] = mapped_column(Boolean, default=True)

    # Site içi (uygulama) bildirimleri
    site_new_subscriber: Mapped[bool] = mapped_column(Boolean, default=True)
    site_new_message: Mapped[bool] = mapped_column(Boolean, default=True)
    site_new_tip: Mapped[bool] = mapped_column(Boolean, default=True)
    site_new_comment: Mapped[bool] = mapped_column(Boolean, default=True)
    site_new_like: Mapped[bool] = mapped_column(Boolean, default=True)
    site_mentions: Mapped[bool] = mapped_column(Boolean, default=True)
    site_new_follower: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # İlişkiler
    user: Mapped["User"] = relationship("User")

