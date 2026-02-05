"""
Abonelik Şemaları (Schemas)
===========================
Bu dosya abonelik ile ilgili Pydantic şemalarını içerir.
Abonelik oluşturma, listeleme ve kampanya yönetimi.

Şemalar:
- SubscriptionCreate: Abonelik oluşturma
- SubscriptionResponse: Abonelik detay yanıtı
- MySubscribersResponse: Abone listesi
- CreatorOfferCreate/Response: Kampanya şemaları
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class SubscriptionType(str, Enum):
    """Abonelik süresi - Ne kadar süreyle abone olunacak"""
    ONE_MONTH = "1_month"       # 1 aylık
    THREE_MONTHS = "3_months"   # 3 aylık
    SIX_MONTHS = "6_months"     # 6 aylık
    TWELVE_MONTHS = "12_months"  # 12 aylık (yıllık)


class SubscriptionStatus(str, Enum):
    """Abonelik durumu - Aboneliğin mevcut hali"""
    ACTIVE = "active"       # Aktif
    EXPIRED = "expired"     # Süresi dolmuş
    CANCELLED = "cancelled"  # İptal edilmiş
    PENDING = "pending"     # Beklemede


class SubscriptionCreate(BaseModel):
    """
    Abonelik Oluşturma Şeması
    -------------------------
    Bir içerik üreticisine abone olmak için.
    """
    creator_id: UUID = Field(..., description="İçerik üreticisi ID'si")
    type: SubscriptionType = Field(default=SubscriptionType.ONE_MONTH, description="Abonelik süresi")
    payment_method: str = Field(..., pattern="^(monero|btcpay|wallet)$", description="Ödeme yöntemi")
    offer_code: Optional[str] = Field(None, description="İndirim/kampanya kodu")


class SubscriptionResponse(BaseModel):
    """
    Abonelik Detay Yanıtı
    ---------------------
    Aboneliğin tüm bilgileri.
    """
    id: UUID
    
    # Taraflar
    subscriber_id: UUID                      # Abone olan
    creator_id: UUID                         # Abone olunan
    creator_username: str                    # İçerik üreticisi kullanıcı adı
    creator_display_name: Optional[str]      # İçerik üreticisi görünen ad
    creator_avatar_url: Optional[str]        # İçerik üreticisi profil resmi
    
    # Abonelik bilgileri
    type: SubscriptionType                   # Süre türü
    status: SubscriptionStatus               # Mevcut durum
    
    # Tarihler
    starts_at: datetime                      # Başlangıç
    expires_at: datetime                     # Bitiş
    cancelled_at: Optional[datetime]         # İptal tarihi
    
    # Ödeme bilgileri
    amount: float                            # Ödenen tutar
    currency: str                            # Para birimi
    payment_method: str                      # Ödeme yöntemi
    
    # Diğer
    auto_renew: bool                         # Otomatik yenileme
    discount_percent: Optional[int]          # Uygulanan indirim
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class MySubscribersResponse(BaseModel):
    """
    Abone Listesi Yanıtı (İçerik Üreticisi için)
    -------------------------------------------
    İçerik üreticisinin abonelerini görmesi için.
    """
    id: UUID
    subscriber_id: UUID                      # Abonenin ID'si
    subscriber_username: str                 # Abonenin kullanıcı adı
    subscriber_display_name: Optional[str]   # Abonenin görünen adı
    subscriber_avatar_url: Optional[str]     # Abonenin profil resmi
    
    status: SubscriptionStatus               # Abonelik durumu
    starts_at: datetime                      # Başlangıç
    expires_at: datetime                     # Bitiş
    
    total_spent: float = 0                   # Bu abonenin toplam harcaması
    
    class Config:
        from_attributes = True


class CreatorOfferCreate(BaseModel):
    """
    Kampanya Oluşturma Şeması
    -------------------------
    İçerik üreticisinin indirimli teklif oluşturması için.
    """
    name: str = Field(..., max_length=100, description="Kampanya adı")
    discount_percent: int = Field(..., ge=5, le=90, description="İndirim yüzdesi (5-90)")
    subscription_type: Optional[SubscriptionType] = Field(None, description="Hangi abonelik türü için geçerli")
    max_uses: Optional[int] = Field(None, ge=1, description="Maksimum kullanım sayısı")
    expires_at: datetime = Field(..., description="Kampanya bitiş tarihi")


class CreatorOfferResponse(BaseModel):
    """
    Kampanya Yanıtı
    ---------------
    Oluşturulan kampanyanın detayları.
    """
    id: UUID
    creator_id: UUID                          # Kampanyayı oluşturan
    
    name: str                                 # Kampanya adı
    discount_percent: int                     # İndirim yüzdesi
    subscription_type: Optional[SubscriptionType]  # Geçerli olduğu abonelik türü
    
    max_uses: Optional[int]                   # Maksimum kullanım
    current_uses: int                         # Şu anki kullanım sayısı
    
    starts_at: datetime
    expires_at: datetime
    
    is_active: bool
    is_valid: bool  # Calculated: active, not expired, not maxed out
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ SUBSCRIPTION PLAN SCHEMAS ============

class SubscriptionPlanCreate(BaseModel):
    """
    Abonelik Planı Oluşturma Şeması
    -------------------------------
    İçerik üreticisinin yeni plan oluşturması için.
    """
    name: str = Field(..., max_length=100, description="Plan adı")
    description: Optional[str] = Field(None, max_length=500, description="Plan açıklaması")
    price: float = Field(..., ge=1.0, description="Aylık fiyat")
    currency: str = Field(default="USD", description="Para birimi")
    duration_months: int = Field(default=1, ge=1, le=12, description="Süre (ay)")
    tier: int = Field(default=1, ge=1, le=10, description="Plan seviyesi")
    is_public: bool = Field(default=True, description="Herkese açık mı")


class SubscriptionPlanUpdate(BaseModel):
    """
    Abonelik Planı Güncelleme Şeması
    --------------------------------
    Mevcut planı güncellemek için.
    """
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=1.0)
    duration_months: Optional[int] = Field(None, ge=1, le=12)
    tier: Optional[int] = Field(None, ge=1, le=10)
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(BaseModel):
    """
    Abonelik Planı Yanıtı
    ---------------------
    Plan detayları.
    """
    id: UUID
    creator_id: UUID
    name: str
    description: Optional[str]
    price: float
    currency: str
    duration_months: int
    tier: int
    is_active: bool
    is_public: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ SUBSCRIPTION BUNDLE SCHEMAS ============

class SubscriptionBundleCreate(BaseModel):
    """
    Abonelik Paketi Oluşturma Şeması
    --------------------------------
    Birden fazla içerik üreticisini içeren paket.
    """
    name: str = Field(..., max_length=100, description="Paket adı")
    description: Optional[str] = Field(None, max_length=500, description="Paket açıklaması")
    price: float = Field(..., ge=1.0, description="İndirimli fiyat")
    original_price: float = Field(..., ge=1.0, description="Normal toplam fiyat")
    currency: str = Field(default="USD", description="Para birimi")
    duration_months: int = Field(default=1, ge=1, le=12, description="Süre (ay)")
    creator_ids: list[UUID] = Field(..., description="Paketteki içerik üreticileri")
    max_purchases: Optional[int] = Field(None, ge=1, description="Maksimum satış sayısı")
    expires_at: Optional[datetime] = Field(None, description="Paket bitiş tarihi")


class SubscriptionBundleResponse(BaseModel):
    """
    Abonelik Paketi Yanıtı
    ----------------------
    Paket detayları.
    """
    id: UUID
    name: str
    description: Optional[str]
    price: float
    original_price: float
    currency: str
    duration_months: int
    is_active: bool
    max_purchases: Optional[int]
    current_purchases: int
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ STATS SCHEMAS ============

class SubscriberStats(BaseModel):
    """
    Abone İstatistikleri
    --------------------
    İçerik üreticisinin abone istatistikleri.
    """
    total_subscribers: int = 0
    active_subscribers: int = 0
    new_this_month: int = 0
    churned_this_month: int = 0
    monthly_revenue: float = 0.0
    lifetime_revenue: float = 0.0
