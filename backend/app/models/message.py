"""
Mesajlaşma Modelleri
====================
Bu dosya direkt mesajlaşma sistemi ile ilgili veritabanı modellerini içerir.

İçerdiği modeller:
- Conversation: İki kullanıcı arasındaki sohbet
- Message: Tekil mesajlar
- MessageMedia: Mesajlara eklenen medya dosyaları
- MassMessage: Birden fazla aboneye gönderilen toplu mesajlar
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin
from app.models.post import MediaType

if TYPE_CHECKING:
    from app.models.user import User


class Conversation(Base):
    """
    Konuşma Modeli
    ==============
    İki kullanıcı arasındaki sohbeti temsil eder.
    Her kullanıcı çifti için tek bir konuşma kaydı vardır.
    Engelleme ve sessize alma özellikleri içerir.
    """
    __tablename__ = "conversations"
    
    # Konuşmanın tarafları
    user1_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user2_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Son mesaj bilgileri (sıralama için)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_message_preview: Mapped[Optional[str]] = mapped_column(String(255))  # Son mesajın önizlemesi
    
    # Okunmamış mesaj sayıları
    user1_unread: Mapped[int] = mapped_column(Integer, default=0)  # User1 için okunmamış
    user2_unread: Mapped[int] = mapped_column(Integer, default=0)  # User2 için okunmamış
    
    # Engelleme durumu
    user1_blocked: Mapped[bool] = mapped_column(Boolean, default=False)  # User1 user2'yi engelledi mi?
    user2_blocked: Mapped[bool] = mapped_column(Boolean, default=False)  # User2 user1'i engelledi mi?
    
    # Sessize alma
    user1_muted: Mapped[bool] = mapped_column(Boolean, default=False)  # User1 bildirimleri kapattı mı?
    user2_muted: Mapped[bool] = mapped_column(Boolean, default=False)  # User2 bildirimleri kapattı mı?
    
    # İlişkiler
    user1: Mapped["User"] = relationship("User", foreign_keys=[user1_id])
    user2: Mapped["User"] = relationship("User", foreign_keys=[user2_id])
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", lazy="dynamic")
    participants: Mapped[List["ConversationParticipant"]] = relationship("ConversationParticipant", back_populates="conversation")
    
    __table_args__ = (
        Index('idx_conversations_user1_id', 'user1_id'),  # User1'e göre arama
        Index('idx_conversations_user2_id', 'user2_id'),  # User2'ye göre arama
        Index('idx_conversations_last_message', 'last_message_at'),  # Son mesaja göre sıralama
        Index('idx_conversations_users', 'user1_id', 'user2_id', unique=True),  # Kullanıcı çifti benzersiz
    )


class Message(Base, SoftDeleteMixin):
    """
    Mesaj Modeli
    ============
    İki kullanıcı arasındaki tekil mesaj.
    PPV (ücretli) mesaj ve bahşiş ekleme özelliği destekler.
    """
    __tablename__ = "messages"
    
    # Hangi konuşmaya ait, kim gönderdi
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Mesaj içeriği
    text: Mapped[Optional[str]] = mapped_column(Text)
    
    # PPV (Pay-Per-View) ücretli mesaj
    is_ppv: Mapped[bool] = mapped_column(Boolean, default=False)      # Ücretli mesaj mı?
    ppv_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # Fiyatı
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=True)  # Kilit açıldı mı?
    
    # Okunma durumu
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)                      # Okundu mu?
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))       # Okunma zamanı
    
    # Mesaja eklenen bahşiş
    tip_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # İlişkiler
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")  # Ait olduğu konuşma
    sender: Mapped["User"] = relationship("User")  # Gönderen
    media: Mapped[List["MessageMedia"]] = relationship("MessageMedia", back_populates="message", cascade="all, delete-orphan")  # Medya dosyaları
    
    # Veritabanı indexleri - Sorgu performansı için
    __table_args__ = (
        Index('idx_messages_conversation_id', 'conversation_id'),  # Konuşma mesajları için
        Index('idx_messages_sender_id', 'sender_id'),              # Gönderici bazlı sorgular
        Index('idx_messages_created_at', 'created_at'),            # Tarih sıralaması
    )


class MessageMedia(Base):
    """
    Mesaj Medya Modeli
    ==================
    Mesajlara eklenen resim, video ve ses dosyaları.
    """
    __tablename__ = "message_media"
    
    # Hangi mesaja ait
    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"))
    
    # Dosya bilgileri
    type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=False)  # Medya türü
    url: Mapped[str] = mapped_column(String(500), nullable=False)               # Dosya URL'i
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))           # Küçük resim
    blur_url: Mapped[Optional[str]] = mapped_column(String(500))                # PPV için bulanık önizleme
    
    # Dosya meta verileri
    filename: Mapped[str] = mapped_column(String(255))        # Orijinal dosya adı
    file_size: Mapped[int] = mapped_column(Integer)           # Dosya boyutu (byte)
    mime_type: Mapped[str] = mapped_column(String(100))       # MIME tipi
    duration: Mapped[Optional[int]] = mapped_column(Integer)  # Video/ses süresi (saniye)
    
    # Sıralama
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # Gösterim sırası
    
    # İlişkiler
    message: Mapped["Message"] = relationship("Message", back_populates="media")
    
    __table_args__ = (
        Index('idx_message_media_message_id', 'message_id'),  # Mesaja göre arama
    )


class MassMessage(Base):
    """
    Toplu Mesaj Modeli
    ==================
    İçerik üreticilerinin birden fazla aboneye aynı anda gönderdiği mesajlar.
    İstatistikler ile gönderim durumu takip edilir.
    """
    __tablename__ = "mass_messages"
    
    # Gönderen içerik üreticisi
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Mesaj içeriği
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # PPV (ücretli mesaj)
    is_ppv: Mapped[bool] = mapped_column(Boolean, default=False)
    ppv_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # İstatistikler
    recipients_count: Mapped[int] = mapped_column(Integer, default=0)  # Toplam alıcı sayısı
    sent_count: Mapped[int] = mapped_column(Integer, default=0)        # Gönderilen sayısı
    read_count: Mapped[int] = mapped_column(Integer, default=0)        # Okunan sayısı
    unlocked_count: Mapped[int] = mapped_column(Integer, default=0)    # Kilidi açılan sayısı (PPV için)
    
    # Gönderim durumu
    is_sending: Mapped[bool] = mapped_column(Boolean, default=False)                   # Şu an gönderiliyor mu?
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # Gönderim tamamlanma zamanı
    
    # İlişkiler
    sender: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_mass_messages_sender_id', 'sender_id'),  # Göndericiye göre arama
    )


class ConversationParticipant(Base):
    """
    Konuşma Katılımcısı Modeli
    ==========================
    Konuşmadaki kullanıcıları ve durumlarını takip eder.
    """
    __tablename__ = "conversation_participants"
    
    # Hangi konuşma, hangi kullanıcı
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Katılımcı durumu
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)    # Bildirimler kapalı mı
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)  # Engellenmiş mi
    unread_count: Mapped[int] = mapped_column(Integer, default=0)     # Okunmamış mesaj sayısı
    
    # Son görülme
    last_read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # İlişkiler
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="participants")
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_conv_participants_conversation', 'conversation_id'),
        Index('idx_conv_participants_user', 'user_id'),
        Index('idx_conv_participants_unique', 'conversation_id', 'user_id', unique=True),
    )
