"""
Gönderi Şemaları (Schemas)
===========================
Bu dosya gönderi/içerik ile ilgili Pydantic şemalarını içerir.
API istekleri ve yanıtları için veri doğrulama ve serileştirme sağlar.

Şemalar:
- PostCreate/Update: Gönderi oluşturma/güncelleme
- PostResponse: Gönderi detay yanıtı
- PostMediaResponse: Medya bilgileri
- CommentCreate/Response: Yorum şemaları
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class MediaType(str, Enum):
    """Medya türü - Gönderideki dosya tipi"""
    IMAGE = "image"  # Resim/fotoğraf
    VIDEO = "video"  # Video
    AUDIO = "audio"  # Ses dosyası


class PostMediaResponse(BaseModel):
    """
    Gönderi Medya Yanıtı
    --------------------
    Gönderiye eklenmiş medya dosyasının bilgileri.
    Kilitli içerik için blur_url gösterilir.
    """
    id: UUID
    type: MediaType                # Medya türü
    url: str                       # Dosya URL'i
    thumbnail_url: Optional[str]   # Küçük resim
    blur_url: Optional[str]        # Bulanık önizleme (PPV için)
    duration: Optional[int]        # Video/ses süresi (saniye)
    width: Optional[int]           # Genişlik (piksel)
    height: Optional[int]          # Yükseklik (piksel)
    is_locked: bool = False        # İçerik kilitli mi? (PPV)
    
    class Config:
        from_attributes = True


class PostAuthorResponse(BaseModel):
    """
    Gönderi Yazarı Mini Yanıtı
    --------------------------
    Gönderinin yazarının temel bilgileri.
    """
    id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    is_verified_creator: bool  # Doğrulanmış mı?
    
    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    """
    Gönderi Oluşturma Şeması
    ------------------------
    Yeni gönderi oluşturmak için gerekli bilgiler.
    PPV ve zamanlama özellikleri desteklenir.
    """
    text: Optional[str] = Field(None, max_length=5000, description="Gönderi içeriği")
    media_ids: List[UUID] = Field(default=[], description="Yüklenmiş medya ID'leri")
    
    # PPV (Pay-Per-View) ayarları
    is_ppv: bool = Field(default=False, description="Ücretli içerik mi?")
    ppv_price: Optional[float] = Field(None, ge=1, le=500, description="PPV fiyatı (1-500)")
    is_free_for_subscribers: bool = Field(default=True, description="Aboneler ücretsiz görsün mü?")
    
    # Zamanlama
    release_date: Optional[datetime] = Field(None, description="Zamanlanmış yayın tarihi")
    expire_date: Optional[datetime] = Field(None, description="Sona erme tarihi")


class PostUpdate(BaseModel):
    """
    Gönderi Güncelleme Şeması
    -------------------------
    Mevcut gönderiyi güncellemek için.
    Sadece gönderilen alanlar güncellenir.
    """
    text: Optional[str] = Field(None, max_length=5000)
    is_ppv: Optional[bool] = None
    ppv_price: Optional[float] = Field(None, ge=1, le=500)
    is_free_for_subscribers: Optional[bool] = None
    is_pinned: Optional[bool] = None  # Profilde sabitle


class PostResponse(BaseModel):
    """
    Gönderi Detay Yanıtı
    --------------------
    Gönderinin tüm bilgileri ve kullanıcıya özel durumlar.
    """
    id: UUID
    author: PostAuthorResponse  # Yazar bilgileri
    
    # İçerik
    text: Optional[str]        # Ham metin
    text_html: Optional[str]   # HTML formatında
    
    media: List[PostMediaResponse]  # Medya dosyaları
    
    # PPV ayarları
    is_ppv: bool
    ppv_price: Optional[float]
    is_free_for_subscribers: bool
    is_pinned: bool  # Sabitlenmiş mi?
    
    # İstatistikler
    likes_count: int      # Beğeni sayısı
    comments_count: int   # Yorum sayısı
    tips_total: float     # Toplam bahşiş
    
    # Kullanıcıya özel durumlar
    is_liked: bool = False      # Beğendim mi?
    is_bookmarked: bool = False  # Kaydettim mi?
    is_unlocked: bool = True    # İçeriği görebiliyor muyum?
    can_comment: bool = True    # Yorum yapabilir miyim?
    
    # Tarihler
    created_at: datetime
    release_date: Optional[datetime]
    expire_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """
    Gönderi Listesi Yanıtı
    ----------------------
    Sayfalanmış gönderi listesi.
    """
    posts: List[PostResponse]  # Gönderiler
    total: int                 # Toplam gönderi sayısı
    page: int                  # Mevcut sayfa
    per_page: int              # Sayfa başına gönderi
    has_more: bool             # Daha fazla var mı?


class CommentCreate(BaseModel):
    """
    Yorum Oluşturma Şeması
    ----------------------
    Gönderiye yorum yapmak için.
    parent_id ile yanıt yorumu yapılabilir.
    """
    text: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[UUID] = None  # Yanıt ise üst yorumun ID'si


class CommentAuthorResponse(BaseModel):
    """
    Yorum Yazarı Mini Yanıtı
    ------------------------
    Yorumu yazan kullanıcının temel bilgileri.
    """
    id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """
    Yorum Yanıtı
    ------------
    Yorumun tüm bilgileri.
    """
    id: UUID
    user: CommentAuthorResponse  # Yorumu yazan
    text: str                    # Yorum metni
    likes_count: int             # Beğeni sayısı
    is_liked: bool = False       # Beğendim mi?
    
    parent_id: Optional[UUID]    # Üst yorum (yanıtsa)
    replies_count: int = 0       # Yanıt sayısı
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """
    Yorum Listesi Yanıtı
    --------------------
    Sayfalanmış yorum listesi.
    """
    comments: List[CommentResponse]  # Yorumlar
    total: int                       # Toplam yorum sayısı
    page: int                        # Mevcut sayfa
    per_page: int                    # Sayfa başına yorum
    has_more: bool                   # Daha fazla var mı?


class ReactionCreate(BaseModel):
    """
    Tepki/Beğeni Oluşturma Şeması
    -----------------------------
    Gönderiye tepki vermek için.
    Desteklenen tepkiler: like, love, fire, laugh, sad
    """
    reaction_type: str = Field(default="like", pattern="^(like|love|fire|laugh|sad)$")
