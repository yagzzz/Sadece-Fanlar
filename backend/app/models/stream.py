"""
Canlı Yayın Modelleri
====================
Bu dosya canlı yayın (live stream) ile ilgili veritabanı modellerini içerir.

İçerdiği modeller:
- StreamStatus: Yayın durumu (planlandı, canlı, bitti, iptal)
- StreamAccessType: Yayın erişim türü (ücretsiz, abone, ücretli)
- Stream: Ana yayın bilgileri
- StreamMessage: Yayın sohbet mesajları
- StreamAccessRecord: Ücretli yayınlara erişim kaydı
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class StreamStatus(str, Enum):
    """Yayın durumu - Yayının şu anki hali"""
    PENDING = "pending"      # Başlatıldı, henüz canlı değil
    SCHEDULED = "scheduled"  # Planlandı, henüz başlamadı
    LIVE = "live"           # Şu an canlı yayında
    ENDED = "ended"         # Yayın sona erdi
    CANCELLED = "cancelled"  # Yayın iptal edildi


class StreamAccessType(str, Enum):
    """Yayın erişim türleri - Kimler izleyebilir"""
    FREE = "free"              # Herkes ücretsiz izleyebilir
    SUBSCRIBERS = "subscribers"  # Sadece aboneler
    PAID = "paid"              # Ücretli bilet gerekli


class StreamType(str, Enum):
    """Yayın türü"""
    LIVE = "live"          # Canlı yayın
    SCHEDULED = "scheduled"  # Planlanmış yayın
    VOD = "vod"            # Video on Demand


class Stream(Base):
    """
    Canlı Yayın Modeli
    ==================
    İçerik üreticilerinin canlı yayın yapmasını sağlar.
    RTMP ile yayın alır, HLS ile izleyicilere sunar.
    Kayıt özelliği ile yayın sonrası VOD olarak izlenebilir.
    """
    __tablename__ = "streams"
    
    # Yayını yapan içerik üreticisi
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Yayın bilgileri
    title: Mapped[str] = mapped_column(String(255), nullable=False)  # Yayın başlığı
    description: Mapped[Optional[str]] = mapped_column(Text)  # Yayın açıklaması
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))  # Kapak resmi
    
    # Durum bilgisi
    status: Mapped[StreamStatus] = mapped_column(SQLEnum(StreamStatus), default=StreamStatus.SCHEDULED)
    
    # Zamanlama bilgileri
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # Planlanan başlangıç
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))    # Gerçek başlangıç
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))      # Bitiş zamanı
    
    # Erişim kontrolü - Yayını kimlerin izleyebileceği
    access: Mapped[StreamAccessType] = mapped_column(SQLEnum(StreamAccessType), default=StreamAccessType.SUBSCRIBERS)
    price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # Ücretli ise fiyat
    
    # Yayın teknik ayarları
    stream_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # Benzersiz yayın anahtarı (OBS'ye girilen)
    rtmp_url: Mapped[Optional[str]] = mapped_column(String(500))  # Yayıncının bağlanacağı RTMP adresi
    hls_url: Mapped[Optional[str]] = mapped_column(String(500))   # İzleyicilerin izleyeceği HLS adresi
    
    # VOD (Video on Demand) - Yayın kaydı ayarları
    save_vod: Mapped[bool] = mapped_column(Boolean, default=True)  # Yayın kaydedilsin mi?
    vod_url: Mapped[Optional[str]] = mapped_column(String(500))    # Kaydedilen video adresi
    
    # İstatistikler
    viewers_count: Mapped[int] = mapped_column(Integer, default=0)   # Anlık izleyici sayısı
    peak_viewers: Mapped[int] = mapped_column(Integer, default=0)    # En yüksek anlık izleyici
    total_viewers: Mapped[int] = mapped_column(Integer, default=0)   # Toplam izleyici (benzersiz)
    tips_total: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), default=0)  # Toplam bahşiş
    duration: Mapped[Optional[int]] = mapped_column(Integer)  # Yayın süresi (saniye)
    
    # İlişkiler
    creator: Mapped["User"] = relationship("User", back_populates="streams")  # Yayıncı
    messages: Mapped[List["StreamMessage"]] = relationship("StreamMessage", back_populates="stream", lazy="dynamic")  # Sohbet
    
    __table_args__ = (
        Index('idx_streams_creator_id', 'creator_id'),      # Yayıncıya göre arama
        Index('idx_streams_status', 'status'),              # Duruma göre filtreleme
        Index('idx_streams_scheduled_at', 'scheduled_at'),  # Tarihe göre sıralama
        Index('idx_streams_stream_key', 'stream_key'),      # Stream key ile arama
    )


class StreamMessage(Base):
    """
    Yayın Sohbet Mesajı
    ===================
    Canlı yayın sırasında izleyicilerin gönderdiği mesajlar.
    Bahşiş gönderme özelliği de bu mesajlar üzerinden yapılır.
    """
    __tablename__ = "stream_messages"
    
    # Hangi yayında, kim yazdı
    stream_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("streams.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Mesaj içeriği
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Bahşiş eklenmişse tutarı
    tip_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # Moderasyon - Silinen mesajlar için
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # Silindi mi?
    deleted_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))  # Kim sildi?
    
    # Relationships - İlişkiler
    stream: Mapped["Stream"] = relationship("Stream", back_populates="messages")  # Ait olduğu yayın
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])  # Mesajı yazan kullanıcı
    
    __table_args__ = (
        Index('idx_stream_messages_stream_id', 'stream_id'),  # Yayına göre arama
        Index('idx_stream_messages_created_at', 'created_at'),  # Tarihe göre arama
    )


class StreamAccessRecord(Base):
    """
    Ücretli yayınlara erişim kaydı
    Kim, hangi yayına, nasıl erişim aldı bilgisini tutar
    """
    __tablename__ = "stream_accesses"
    
    stream_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("streams.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Erişim nasıl alındı
    access_type: Mapped[str] = mapped_column(String(20))  # paid=ücretli, subscription=abonelik, free=ücretsiz
    amount_paid: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # Ödenen tutar
    
    __table_args__ = (
        Index('idx_stream_accesses_stream_user', 'stream_id', 'user_id', unique=True),  # Her kullanıcı yayına 1 kez erişim alır
    )


# Alias for backwards compatibility
LiveStream = Stream


class StreamViewer(Base):
    """
    Yayın İzleyici Kaydı
    ====================
    Canlı yayını izleyen kullanıcıların kaydı.
    """
    __tablename__ = "stream_viewers"
    
    stream_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("streams.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # İzleme bilgileri
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    watch_duration: Mapped[int] = mapped_column(Integer, default=0)  # İzleme süresi (saniye)
    
    # İlişkiler
    stream: Mapped["Stream"] = relationship("Stream")
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_stream_viewers_stream_id', 'stream_id'),
        Index('idx_stream_viewers_user_id', 'user_id'),
    )


class StreamTip(Base):
    """
    Yayın Bahşişi
    =============
    Canlı yayın sırasında gönderilen bahşişler.
    """
    __tablename__ = "stream_tips"
    
    stream_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("streams.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Bahşiş bilgileri
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    message: Mapped[Optional[str]] = mapped_column(String(500))
    
    # İlişkiler
    stream: Mapped["Stream"] = relationship("Stream")
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_stream_tips_stream_id', 'stream_id'),
        Index('idx_stream_tips_user_id', 'user_id'),
    )


class ScheduledStream(Base):
    """
    Planlanmış Yayın
    ================
    Gelecekte yapılacak yayınların planlaması.
    """
    __tablename__ = "scheduled_streams"
    
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Yayın bilgileri
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Zamanlama
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_estimate: Mapped[Optional[int]] = mapped_column(Integer)  # Tahmini süre (dakika)
    
    # Erişim kontrolü
    access: Mapped[StreamAccessType] = mapped_column(SQLEnum(StreamAccessType), default=StreamAccessType.SUBSCRIBERS)
    price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # Durum
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    actual_stream_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("streams.id"))
    
    # Hatırlatma
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # İlişkiler
    creator: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_scheduled_streams_creator_id', 'creator_id'),
        Index('idx_scheduled_streams_scheduled_at', 'scheduled_at'),
    )
