"""
Gönderi ve İçerik Modelleri
===========================
Bu dosya kullanıcıların paylaştığı içeriklerle ilgili veritabanı modellerini içerir.

İçerdiği modeller:
- PostStatus: Gönderi durumu (taslak, beklemede, onaylandı, reddedildi)
- MediaType: Medya türü (resim, video, ses)
- Post: Ana gönderi/içerik modeli
- PostMedia: Gönderilere eklenen medya dosyaları
- PostComment: Gönderi yorumları
- PostReaction: Beğeniler ve tepkiler
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.content import Attachment


class PostStatus(str, Enum):
    """Gönderi durumu - İçeriğin yayın aşaması"""
    DRAFT = "draft"         # Taslak - Henüz yayınlanmadı
    PENDING = "pending"     # Beklemede - Onay bekliyor
    APPROVED = "approved"   # Onaylandı - Yayında
    REJECTED = "rejected"   # Reddedildi - Yayınlanmadı
    SCHEDULED = "scheduled"  # Zamanlandı - İleri tarihte yayınlanacak
    REMOVED = "removed"      # Kaldırıldı - Silinmiş/geri çekilmiş


class MediaType(str, Enum):
    """Medya türü - Gönderideki dosya tipi"""
    IMAGE = "image"  # Resim/fotoğraf
    VIDEO = "video"  # Video
    AUDIO = "audio"  # Ses dosyası


class Post(Base, SoftDeleteMixin):
    """
    Gönderi/İçerik Modeli
    =====================
    İçerik üreticilerinin paylaştığı gönderiler.
    Metin, resim, video veya ses içerebilir.
    PPV (pay-per-view) ile ücretli içerik satışı yapılabilir.
    """
    __tablename__ = "posts"
    
    # Gönderiyi paylaşan içerik üreticisi
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # İçerik metni
    text: Mapped[Optional[str]] = mapped_column(Text)  # Ham metin
    text_html: Mapped[Optional[str]] = mapped_column(Text)  # Markdown'dan HTML'e dönüştürülmüş
    
    # Durum bilgisi
    status: Mapped[PostStatus] = mapped_column(SQLEnum(PostStatus), default=PostStatus.APPROVED)
    
    # Zamanlama
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # Yayın tarihi
    expire_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))   # Son geçerlilik
    
    # Ücretlendirme
    is_ppv: Mapped[bool] = mapped_column(Boolean, default=False)  # Ücretli içerik mi?
    ppv_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # PPV fiyatı
    is_free_for_subscribers: Mapped[bool] = mapped_column(Boolean, default=True)  # Aboneler ücretsiz görebilir mi?
    
    # Görüntüleme
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)  # Profilde sabitlenmiş mi?
    
    # İstatistikler (performans için denormalize edilmiş)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)     # Beğeni sayısı
    comments_count: Mapped[int] = mapped_column(Integer, default=0)  # Yorum sayısı
    views_count: Mapped[int] = mapped_column(Integer, default=0)     # Görüntülenme sayısı
    tips_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)  # Toplam bahşiş
    
    # İlişkiler
    author: Mapped["User"] = relationship("User", back_populates="posts")  # Yazar
    media: Mapped[List["PostMedia"]] = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")  # Medya dosyaları
    comments: Mapped[List["PostComment"]] = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")  # Yorumlar
    reactions: Mapped[List["PostReaction"]] = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")  # Tepkiler
    
    # Veritabanı indexleri - Sorgu performansı için
    __table_args__ = (
        Index('idx_posts_author_id', 'author_id'),     # Yazar bazlı sorgular için
        Index('idx_posts_created_at', 'created_at'),   # Tarih sıralaması için
        Index('idx_posts_status', 'status'),           # Durum filtrelemesi için
        Index('idx_posts_is_pinned', 'is_pinned'),     # Sabitlenen postlar için
    )
    
    def __repr__(self):
        return f"<Post {self.id} by {self.author_id}>"

class PostMedia(Base):
    """
    Gönderi Medya Modeli
    ====================
    Gönderilere eklenen resim, video ve ses dosyaları.
    Video işleme, HLS streaming ve blur preview desteği içerir.
    """
    __tablename__ = "post_media"
    
    # Hangi gönderiye ait
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    
    # Dosya bilgileri
    type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=False)  # Medya türü
    url: Mapped[str] = mapped_column(String(500), nullable=False)  # Dosya URL'i
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))  # Küçük resim
    blur_url: Mapped[Optional[str]] = mapped_column(String(500))  # PPV için bulanık önizleme
    
    # Dosya meta verileri
    filename: Mapped[str] = mapped_column(String(255))  # Orijinal dosya adı
    file_size: Mapped[int] = mapped_column(Integer)  # Dosya boyutu (byte)
    mime_type: Mapped[str] = mapped_column(String(100))  # MIME tipi (image/jpeg, video/mp4, vb.)
    
    # Video özel alanları
    duration: Mapped[Optional[int]] = mapped_column(Integer)  # Video süresi (saniye)
    width: Mapped[Optional[int]] = mapped_column(Integer)     # Genişlik (piksel)
    height: Mapped[Optional[int]] = mapped_column(Integer)    # Yükseklik (piksel)
    
    # İşleme durumu
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)  # İşlendi mi?
    processing_error: Mapped[Optional[str]] = mapped_column(Text)  # İşleme hatası varsa
    
    # HLS streaming (videolar için uyarlanabilir akış)
    hls_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Sıralama
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # Gösterim sırası
    
    # İlişkiler
    post: Mapped["Post"] = relationship("Post", back_populates="media")
    
    __table_args__ = (
        Index('idx_post_media_post_id', 'post_id'),  # Gönderiye göre arama
    )


class PostComment(Base, SoftDeleteMixin):
    """
    Gönderi Yorum Modeli
    ====================
    Gönderilere yapılan yorumlar.
    Hiyerarşik yapı ile yanıt yorumlarını destekler.
    """
    __tablename__ = "post_comments"
    
    # Hangi gönderiye, kim yazdı
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("post_comments.id"))  # Yanıt ise üst yorum
    
    # Yorum içeriği
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # İstatistikler
    likes_count: Mapped[int] = mapped_column(Integer, default=0)  # Beğeni sayısı
    
    # İlişkiler
    post: Mapped["Post"] = relationship("Post", back_populates="comments")  # Ait olduğu gönderi
    user: Mapped["User"] = relationship("User")  # Yorumu yazan
    parent: Mapped[Optional["PostComment"]] = relationship("PostComment", remote_side="PostComment.id")  # Üst yorum
    replies: Mapped[List["PostComment"]] = relationship("PostComment", back_populates="parent")  # Yanıtlar
    
    __table_args__ = (
        Index('idx_post_comments_post_id', 'post_id'),  # Gönderiye göre arama
        Index('idx_post_comments_user_id', 'user_id'),  # Kullanıcıya göre arama
    )


class PostReaction(Base):
    """
    Gönderi Tepki/Beğeni Modeli
    ===========================
    Gönderilere verilen beğeniler ve tepkiler.
    Bir kullanıcı bir gönderiye sadece bir tepki verebilir.
    """
    __tablename__ = "post_reactions"
    
    # Hangi gönderiye, kim tepki verdi
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Tepki türü - like, love, fire, vb.
    reaction_type: Mapped[str] = mapped_column(String(20), default="like")
    
    # İlişkiler
    post: Mapped["Post"] = relationship("Post", back_populates="reactions")
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_post_reactions_post_id', 'post_id'),  # Gönderiye göre arama
        Index('idx_post_reactions_user_id_post_id', 'user_id', 'post_id', unique=True),  # Kullanıcı başına tek tepki
    )
