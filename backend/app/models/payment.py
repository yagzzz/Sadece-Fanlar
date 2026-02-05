"""
Payment related models
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.transaction import PaymentMethod

if TYPE_CHECKING:
    from app.models.user import User


class PaymentRequestStatus(str, Enum):
    PENDING = "pending"
    AWAITING_PAYMENT = "awaiting_payment"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class PaymentRequestType(str, Enum):
    DEPOSIT = "deposit"
    SUBSCRIPTION = "subscription"
    TIP = "tip"
    POST_UNLOCK = "post_unlock"
    MESSAGE_UNLOCK = "message_unlock"
    STREAM_ACCESS = "stream_access"


class PaymentRequest(Base):
    """Payment request for crypto payments"""
    __tablename__ = "payment_requests"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Type
    type: Mapped[PaymentRequestType] = mapped_column(SQLEnum(PaymentRequestType), nullable=False)
    status: Mapped[PaymentRequestStatus] = mapped_column(
        SQLEnum(PaymentRequestStatus), 
        default=PaymentRequestStatus.PENDING
    )
    
    # Amount
    amount_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    amount_crypto: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))
    crypto_currency: Mapped[str] = mapped_column(String(10))  # XMR, BTC
    exchange_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))
    
    # Payment method
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)
    
    # Monero specific
    monero_address: Mapped[Optional[str]] = mapped_column(String(100))
    monero_payment_id: Mapped[Optional[str]] = mapped_column(String(64))
    monero_integrated_address: Mapped[Optional[str]] = mapped_column(String(110))
    
    # BTCPay specific
    btcpay_invoice_id: Mapped[Optional[str]] = mapped_column(String(100))
    btcpay_checkout_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Related entity
    reference_type: Mapped[Optional[str]] = mapped_column(String(50))
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    recipient_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Expiry
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Transaction tracking
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255))
    confirmations: Mapped[int] = mapped_column(default=0)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Additional data
    payment_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)  # metadata is reserved in SQLAlchemy
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    recipient: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recipient_id])
    
    __table_args__ = (
        Index('idx_payment_requests_user_id', user_id),
        Index('idx_payment_requests_status', status),
        Index('idx_payment_requests_monero_address', monero_address),
        Index('idx_payment_requests_btcpay_invoice', btcpay_invoice_id),
        Index('idx_payment_requests_expires_at', expires_at),
    )


class Invoice(Base):
    """Invoice for transactions"""
    __tablename__ = "invoices"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Invoice number
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Amount
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    
    # Status
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Related
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    
    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    line_items: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # PDF
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_invoices_user_id', user_id),
        Index('idx_invoices_number', invoice_number),
    )
