"""
Temel model sınıfı - Tüm modeller için ortak işlevsellik
Base model class - Common functionality for all models
"""
import uuid
from datetime import datetime
from typing import Any, ClassVar
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Tüm modeller için temel sınıf
    Base class for all database models
    
    Her model için otomatik olarak:
    - UUID tipinde benzersiz id
    - created_at (oluşturulma zamanı)
    - updated_at (güncellenme zamanı)
    alanları sağlar
    """
    
    # Alt sınıflar kendi __tablename__'lerini tanımlayacak
    # Subclasses will define their own __tablename__
    __tablename__: ClassVar[str]
    
    # Benzersiz kimlik - Primary key with UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Oluşturulma zamanı - Creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Güncellenme zamanı - Update timestamp
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def to_dict(self) -> dict[str, Any]:
        """
        Modeli sözlük formatına çevirir
        Converts model instance to dictionary
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SoftDeleteMixin:
    """
    Yumuşak silme işlevi - Soft delete functionality
    Kayıt silinmez, sadece deleted_at alanı doldurulur
    Record is not deleted, only deleted_at field is set
    """
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )
    
    @property
    def is_deleted(self) -> bool:
        """Kaydın silinip silinmediğini kontrol eder"""
        return self.deleted_at is not None
    
    def soft_delete(self):
        """Kaydı yumuşak siler (deleted_at'i şimdiki zamana ayarlar)"""
        self.deleted_at = datetime.utcnow()


class SlugMixin:
    """
    URL-dostu slug alanı sağlar
    Provides URL-friendly slug field
    """
    slug: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
        index=True
    )
