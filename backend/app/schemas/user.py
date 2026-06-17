"""
Kullanıcı Şemaları (Schemas)
============================
Bu dosya kullanıcı ile ilgili Pydantic şemalarını içerir.
API istekleri ve yanıtları için veri doğrulama ve serileştirme sağlar.

Şemalar:
- UserCreate: Kayıt isteği
- UserLogin: Giriş isteği
- TokenResponse: JWT token yanıtı
- UserResponse: Kullanıcı profil yanıtı
- UserUpdate: Profil güncelleme isteği
- TwoFactorSetup/Verify: 2FA şemaları
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    """
    Kullanıcı Kayıt Şeması
    ----------------------
    Yeni kullanıcı kaydı için gerekli bilgiler.
    Username ve password doğrulaması yapılır.
    """
    username: str = Field(..., min_length=3, max_length=30, description="Kullanıcı adı")
    # E-posta ANONİMLİK için opsiyoneldir. Boş bırakılırsa hesap tamamen anonimdir.
    email: Optional[EmailStr] = Field(None, description="E-posta adresi (isteğe bağlı)")
    password: str = Field(..., min_length=8, max_length=100, description="Şifre")
    display_name: Optional[str] = Field(None, max_length=100, description="Görünen ad")
    referral_code: Optional[str] = Field(None, max_length=20, description="Referans kodu")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Kullanıcı adı doğrulama:
        - Sadece harf, rakam ve alt çizgi
        - Yasaklı isimler kullanılamaz
        """
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir')
        if v.lower() in ['admin', 'root', 'system', 'moderator', 'support']:
            raise ValueError('Bu kullanıcı adı kullanılamaz')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Şifre güvenlik doğrulama:
        - En az bir büyük harf
        - En az bir küçük harf
        - En az bir rakam
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v


class UserLogin(BaseModel):
    """
    Kullanıcı Giriş Şeması
    ----------------------
    Giriş için kullanıcı adı/e-posta ve şifre gerekir.
    2FA etkinse kod da gönderilmeli.
    """
    username: str = Field(..., description="Kullanıcı adı veya e-posta")
    password: str = Field(..., description="Şifre")
    two_factor_code: Optional[str] = Field(None, description="2FA kodu (etkinse)")


class TokenResponse(BaseModel):
    """
    JWT Token Yanıt Şeması
    ----------------------
    Başarılı giriş sonrası dönen token bilgileri.
    access_token kısa ömürlü, refresh_token ile yenilenir.
    """
    access_token: str      # Kısa ömürlü erişim token'ı
    refresh_token: str     # Uzun ömürlü yenileme token'ı
    token_type: str = "bearer"  # Token tipi (her zaman "bearer")
    expires_in: int = 1800      # Token ömrü (saniye, 30 dakika)
    requires_2fa: bool = False  # 2FA doğrulaması gerekli mi?


class RefreshTokenRequest(BaseModel):
    """
    Token Yenileme İsteği
    ---------------------
    Süresi dolan access_token'ı yenilemek için refresh_token gönderilir.
    """
    refresh_token: str


class UserResponse(BaseModel):
    """
    Kullanıcı Yanıt Şeması (Kendi Profili)
    --------------------------------------
    Kullanıcının kendi profil bilgilerini görüntülemesi için.
    E-posta, 2FA durumu gibi gizli bilgiler de dahil.
    """
    id: UUID
    username: str
    email: Optional[str] = None
    display_name: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    website: Optional[str]
    avatar_url: Optional[str]
    cover_url: Optional[str]
    
    # İçerik üreticisi bilgileri
    is_creator: bool              # İçerik üreticisi mi?
    is_verified_creator: bool     # Doğrulanmış içerik üreticisi mi?
    is_free_profile: bool         # Ücretsiz profil mi?
    subscription_price: Optional[float]      # Aylık abonelik fiyatı
    subscription_price_3m: Optional[float]   # 3 aylık fiyat
    subscription_price_6m: Optional[float]   # 6 aylık fiyat
    subscription_price_12m: Optional[float]  # Yıllık fiyat
    
    # Doğrulama durumu
    is_email_verified: bool       # E-posta doğrulandı mı?
    two_factor_enabled: bool      # 2FA etkin mi?
    
    # İstatistikler
    posts_count: int              # Gönderi sayısı
    subscribers_count: int        # Abone sayısı
    subscriptions_count: int      # Takip ettikleri
    likes_count: int              # Aldığı beğeni sayısı
    
    # Referans sistemi
    referral_code: Optional[str]  # Referans kodu
    
    # Tarihler
    created_at: datetime          # Kayıt tarihi
    last_active_at: Optional[datetime]  # Son aktiflik
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """
    Herkese Açık Profil Şeması
    --------------------------
    Diğer kullanıcıların görüntüleyebildiği profil bilgileri.
    E-posta gibi gizli bilgiler dahil değil.
    """
    id: UUID
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    website: Optional[str]
    avatar_url: Optional[str]
    cover_url: Optional[str]
    
    # İçerik üreticisi bilgileri
    is_creator: bool
    is_verified_creator: bool
    is_free_profile: bool
    subscription_price: Optional[float]
    subscription_price_3m: Optional[float]
    subscription_price_6m: Optional[float]
    subscription_price_12m: Optional[float]
    
    # İstatistikler
    posts_count: int
    subscribers_count: Optional[int]  # Gizli olabilir
    likes_count: int
    
    # Mevcut kullanıcının durumu
    is_subscribed: bool = False  # Bu profile abone mi?
    is_following: bool = False   # Bu profili takip ediyor mu?
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Profil Güncelleme Şeması
    ------------------------
    Kullanıcının profil bilgilerini güncellemek için.
    Sadece gönderilen alanlar güncellenir.
    """
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    
    # İçerik üreticisi ayarları
    subscription_price: Optional[float] = Field(None, ge=0, le=1000)       # Aylık fiyat (0-1000)
    subscription_price_3m: Optional[float] = Field(None, ge=0, le=3000)    # 3 aylık
    subscription_price_6m: Optional[float] = Field(None, ge=0, le=6000)    # 6 aylık
    subscription_price_12m: Optional[float] = Field(None, ge=0, le=12000)  # Yıllık
    is_free_profile: Optional[bool] = None  # Ücretsiz profile geç
    
    # Gizlilik ayarları
    is_public_profile: Optional[bool] = None        # Profil herkese açık mı?
    show_subscribers_count: Optional[bool] = None   # Abone sayısı görünsün mü?
    allow_comments: Optional[bool] = None           # Yorumlara izin ver


class BecomeCreatorRequest(BaseModel):
    """
    İçerik Üreticisi Olma İsteği
    ----------------------------
    Normal kullanıcının içerik üreticisi olması için gerekli bilgiler.
    GİZLİLİK: Gerçek isim, kimlik belgesi veya yüz fotoğrafı İSTENMEZ.
    Yasal asgari olarak yalnızca 18+ beyanı alınır.
    """
    display_name: str = Field(..., max_length=100)           # Görünen ad (takma ad olabilir)
    bio: str = Field(..., max_length=1000)                   # Biyografi (zorunlu)
    subscription_price: float = Field(..., ge=0, le=1000)    # Aylık abonelik fiyatı
    categories: List[str] = Field(default_factory=list, max_length=20)  # İçerik kategorileri
    age_confirmed: bool = Field(..., description="18 yaşından büyük olduğunuzu onaylayın")

    @field_validator('age_confirmed')
    @classmethod
    def must_confirm_age(cls, v: bool) -> bool:
        if not v:
            raise ValueError('İçerik üreticisi olmak için 18+ olduğunuzu onaylamalısınız')
        return v


class TwoFactorSetup(BaseModel):
    """
    2FA Kurulum Yanıtı
    ------------------
    2FA etkinleştirme başlatıldığında dönen bilgiler.
    QR kod taranarak authenticator uygulamasına eklenir.
    """
    secret: str             # TOTP secret anahtarı
    qr_code: str           # Base64 kodlanmış QR kod resmi (PNG)
    backup_codes: List[str]  # Yedek kodlar (kaybolursa 2FA'yı atlamak için)


class TwoFactorVerify(BaseModel):
    """
    2FA Doğrulama Şeması
    --------------------
    Authenticator uygulamasından alınan 6 haneli kod.
    """
    code: str = Field(..., min_length=6, max_length=6)  # 6 haneli TOTP kodu


class ChangePassword(BaseModel):
    """
    Şifre Değiştirme İsteği
    -----------------------
    Mevcut şifre ve yeni şifre gerekir.
    Yeni şifre güvenlik kurallarına uymalı.
    """
    current_password: str                                       # Mevcut şifre
    new_password: str = Field(..., min_length=8, max_length=100)  # Yeni şifre
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Yeni şifre güvenlik doğrulama"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v


class UserSearchResult(BaseModel):
    """
    Kullanıcı Arama Sonucu
    ----------------------
    Kullanıcı araması sonucunda dönen minimal bilgiler.
    """
    id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    is_verified_creator: bool      # Doğrulanmış mı?
    subscribers_count: Optional[int]  # Abone sayısı (görünürse)
    
    class Config:
        from_attributes = True
