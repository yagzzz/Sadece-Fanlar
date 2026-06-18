"""
Destek talepleri (ticket) ve Escrow (emanetli özel istek) modelleri.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class TicketStatus(str, Enum):
    OPEN = "open"            # Açık - yanıt bekliyor
    ANSWERED = "answered"    # Yanıtlandı - canlı sohbet açık
    CLOSED = "closed"        # Kapatıldı


class TicketCategory(str, Enum):
    GENERAL = "general"
    PAYMENT = "payment"
    ACCOUNT = "account"
    ABUSE = "abuse"
    OTHER = "other"


class SupportTicket(Base):
    """Kullanıcı destek talebi."""
    __tablename__ = "support_tickets"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[TicketCategory] = mapped_column(SQLEnum(TicketCategory), default=TicketCategory.GENERAL)
    status: Mapped[TicketStatus] = mapped_column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)

    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    messages: Mapped[List["TicketMessage"]] = relationship(
        "TicketMessage", back_populates="ticket", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_tickets_user", "user_id"),
        Index("idx_tickets_status", "status"),
    )


class TicketMessage(Base):
    """Destek talebi içindeki mesajlar (canlı sohbet akışı)."""
    __tablename__ = "ticket_messages"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="messages")
    sender: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("idx_ticket_messages_ticket", "ticket_id"),
    )


class EscrowStatus(str, Enum):
    PENDING = "pending"        # İstek oluşturuldu, üretici onayı bekliyor
    FUNDED = "funded"          # Fan parayı yatırdı (emanette)
    DELIVERED = "delivered"    # Üretici teslim etti, fan onayı bekliyor
    COMPLETED = "completed"    # Tamamlandı, para üreticiye geçti
    DISPUTED = "disputed"      # Anlaşmazlık - yönetici karar verecek
    CANCELLED = "cancelled"    # İptal/iade
    REFUNDED = "refunded"      # Fan'a iade edildi


class EscrowRequest(Base):
    """
    Emanetli özel istek. Fan parayı yatırır, para sitenin emanetinde (pending)
    bekler. Üretici teslim eder, fan onaylayınca para serbest kalır.
    Anlaşmazlıkta yönetici karar verir.
    """
    __tablename__ = "escrow_requests"

    buyer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False), nullable=False)

    status: Mapped[EscrowStatus] = mapped_column(SQLEnum(EscrowStatus), default=EscrowStatus.PENDING)

    delivery_note: Mapped[Optional[str]] = mapped_column(Text)
    delivery_url: Mapped[Optional[str]] = mapped_column(String(500))
    dispute_reason: Mapped[Optional[str]] = mapped_column(Text)

    funded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])

    __table_args__ = (
        Index("idx_escrow_buyer", "buyer_id"),
        Index("idx_escrow_creator", "creator_id"),
        Index("idx_escrow_status", "status"),
    )
