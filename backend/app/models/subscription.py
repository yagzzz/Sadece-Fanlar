"""
Abonelik Modelleri
==================
Bu dosya abonelik sistemi ile ilgili veritabanı modellerini içerir.

İçerdiği modeller:
- SubscriptionStatus: Abonelik durumu (aktif, süresi dolmuş, iptal edildi)
- SubscriptionType: Abonelik süresi (1 ay, 3 ay, 6 ay, 12 ay)
- Subscription: Abone ile içerik üreticisi arasındaki abonelik
- CreatorOffer: İçerik üreticilerinin sunduğu indirimli teklifler
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SubscriptionStatus(str, Enum):
    """Abonelik durumu - Aboneliğin şu anki hali"""
    ACTIVE = "active"       # Aktif - Kullanımda
    EXPIRED = "expired"     # Süresi dolmuş
    CANCELLED = "cancelled"  # İptal edilmiş
    PENDING = "pending"     # Beklemede - Ödeme bekleniyor


class SubscriptionType(str, Enum):
    """Abonelik süresi - Ne kadar süreyle abone olunacak"""
    FREE = "free"                # Ücretsiz abonelik
    PAID = "paid"                # Ücretli abonelik
    TRIAL = "trial"              # Deneme aboneliği
    ONE_MONTH = "1_month"       # 1 aylık
    THREE_MONTHS = "3_months"   # 3 aylık
    SIX_MONTHS = "6_months"     # 6 aylık
    TWELVE_MONTHS = "12_months"  # 12 aylık (yıllık)


class Subscription(Base):
    """
    Abonelik Modeli
    ===============
    Bir kullanıcının bir içerik üreticisine olan aboneliği.
    Kripto para ile ödeme yapılır (Monero veya BTCPay).
    Otomatik yenileme için ön ödemeli bakiye gerekir.
    """
    __tablename__ = "subscriptions"
    
    # Abone olan ve abone olunan
    subscriber_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Abonelik türü ve durumu
    type: Mapped[SubscriptionType] = mapped_column(SQLEnum(SubscriptionType), default=SubscriptionType.ONE_MONTH)
    status: Mapped[SubscriptionStatus] = mapped_column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.PENDING)
    
    # Tarihler
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)   # Başlangıç tarihi
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # Bitiş tarihi
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))     # İptal tarihi
    
    # Ödeme bilgileri
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Ödenen tutar
    currency: Mapped[str] = mapped_column(String(10), default="USD")  # Para birimi
    payment_method: Mapped[str] = mapped_column(String(20))  # monero, btcpay
    
    # Otomatik yenileme (sadece ön ödemeli bakiye ile çalışır)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Uygulanan indirim
    discount_percent: Mapped[Optional[int]] = mapped_column(Integer)  # İndirim yüzdesi
    offer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("creator_offers.id"))  # Kullanılan teklif
    
    # İlişkiler
    subscriber: Mapped["User"] = relationship("User", foreign_keys=[subscriber_id], back_populates="subscriptions")  # Abone
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id], back_populates="subscribers")  # İçerik üreticisi
    offer: Mapped[Optional["CreatorOffer"]] = relationship("CreatorOffer")  # Kullanılan teklif
    
    __table_args__ = (
        Index('idx_subscriptions_subscriber_id', 'subscriber_id'),  # Aboneye göre arama
        Index('idx_subscriptions_creator_id', 'creator_id'),        # İçerik üreticisine göre arama
        Index('idx_subscriptions_status', 'status'),                # Duruma göre filtreleme
        Index('idx_subscriptions_expires_at', 'expires_at'),        # Bitiş tarihine göre sıralama
        Index('idx_subscriptions_subscriber_creator', 'subscriber_id', 'creator_id'),  # Birleşik arama
    )
    
    def __repr__(self):
        return f"<Subscription {self.subscriber_id} -> {self.creator_id}>"


class CreatorOffer(Base):
    """
    İçerik Üreticisi Teklif Modeli
    ==============================
    İçerik üreticilerinin sunduğu sınırlı süreli indirimli abonelik teklifleri.
    Belirli süre veya kullanım limiti ile geçerlidir.
    """
    __tablename__ = "creator_offers"
    
    # Teklifi sunan içerik üreticisi
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Teklif detayları
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Teklif adı (ör: "Yaz İndirimi")
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)  # İndirim yüzdesi (10, 20, 50, vb.)
    
    # Hangi abonelik türleri için geçerli
    subscription_type: Mapped[Optional[SubscriptionType]] = mapped_column(SQLEnum(SubscriptionType))  # None ise hepsi için geçerli
    
    # Kullanım limitleri
    max_uses: Mapped[Optional[int]] = mapped_column(Integer)       # Maksimum kullanım (None = sınırsız)
    current_uses: Mapped[int] = mapped_column(Integer, default=0)  # Şu ana kadar kullanım sayısı
    
    # Geçerlilik süreleri
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)   # Başlangıç tarihi
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # Bitiş tarihi
    
    # Aktiflik durumu
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Manuel olarak devre dışı bırakılabilir
    
    # İlişkiler
    creator: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_creator_offers_creator_id', 'creator_id'),  # İçerik üreticisine göre arama
        Index('idx_creator_offers_active', 'is_active'),       # Aktif teklifleri filtreleme
    )
    
    @property
    def is_valid(self) -> bool:
        """
        Teklifin hala geçerli olup olmadığını kontrol eder.
        Geçerlilik koşulları:
        - is_active True olmalı
        - Şu anki tarih starts_at ve expires_at arasında olmalı
        - max_uses tanımlıysa, current_uses max_uses'dan küçük olmalı
        """
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if now < self.starts_at or now > self.expires_at:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        return True


class SubscriptionPlan(Base):
    """
    Abonelik Planı Modeli
    =====================
    İçerik üreticilerinin sunduğu abonelik planları.
    Her içerik üreticisi birden fazla plan oluşturabilir.
    """
    __tablename__ = "subscription_plans"
    
    # Plan sahibi içerik üreticisi
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Plan detayları
    name: Mapped[str] = mapped_column(String(100), nullable=False)        # Plan adı (ör: "Premium")
    description: Mapped[Optional[str]] = mapped_column(String(500))       # Plan açıklaması
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Fiyat
    currency: Mapped[str] = mapped_column(String(10), default="USD")      # Para birimi
    duration_months: Mapped[int] = mapped_column(Integer, default=1)      # Süre (ay cinsinden)
    
    # Aktiflik ve görünürlük
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)   # Aktif mi
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)   # Herkese açık mı
    
    # İçerik erişim seviyeleri
    tier: Mapped[int] = mapped_column(Integer, default=1)  # Plan seviyesi (1, 2, 3, vb.)
    
    # İlişkiler
    creator: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_subscription_plans_creator_id', 'creator_id'),
        Index('idx_subscription_plans_is_active', 'is_active'),
    )


class SubscriptionBundle(Base):
    """
    Abonelik Paketi Modeli
    ======================
    Birden fazla içerik üreticisini içeren indirimli paketler.
    """
    __tablename__ = "subscription_bundles"
    
    # Paket detayları
    name: Mapped[str] = mapped_column(String(100), nullable=False)         # Paket adı
    description: Mapped[Optional[str]] = mapped_column(String(500))        # Açıklama
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)   # İndirimli fiyat
    original_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Normal fiyat
    currency: Mapped[str] = mapped_column(String(10), default="USD")       # Para birimi
    duration_months: Mapped[int] = mapped_column(Integer, default=1)       # Süre
    
    # Aktiflik
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Sınırlı teklif
    max_purchases: Mapped[Optional[int]] = mapped_column(Integer)
    current_purchases: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
