"""
İşlem, Cüzdan ve Para Çekme Modelleri
=====================================
Bu dosya tüm finansal işlemlerle ilgili veritabanı modellerini içerir.

İçerdiği modeller:
- TransactionType: İşlem türleri (yatırma, abonelik, bahşiş, çekme, vb.)
- TransactionStatus: İşlem durumları (beklemede, işleniyor, tamamlandı, başarısız)
- PaymentMethod: Ödeme yöntemleri (Monero, BTCPay, iç bakiye)
- WithdrawalStatus: Para çekme durumları
- Wallet: Kullanıcı cüzdanı/bakiyesi
- Transaction: Tüm finansal işlemler
- Withdrawal: Para çekme talepleri
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class TransactionType(str, Enum):
    """İşlem türü - Finansal işlemin ne tür bir hareket olduğu"""
    # Gelen ödemeler
    DEPOSIT = "deposit"                      # Para yatırma
    SUBSCRIPTION = "subscription"            # Yeni abonelik ödemesi
    SUBSCRIPTION_RENEWAL = "subscription_renewal"  # Abonelik yenileme
    TIP = "tip"                              # Gönderi bahşişi
    CHAT_TIP = "chat_tip"                    # Sohbet bahşişi
    POST_UNLOCK = "post_unlock"              # Gönderi kilit açma (PPV)
    MESSAGE_UNLOCK = "message_unlock"        # Mesaj kilit açma (PPV)
    STREAM_ACCESS = "stream_access"          # Canlı yayın erişimi
    MESSAGE = "message"                      # Mesaj ücreti/ödemesi
    STREAM_TIP = "stream_tip"                # Canlı yayın bahşişi
    
    # Giden ödemeler
    WITHDRAWAL = "withdrawal"                # Para çekme
    REFUND = "refund"                        # İade
    
    # Dahili işlemler
    REFERRAL_BONUS = "referral_bonus"        # Referans bonusu
    PLATFORM_FEE = "platform_fee"            # Platform komisyonu


class TransactionStatus(str, Enum):
    """İşlem durumu - Finansal işlemin şu anki hali"""
    PENDING = "pending"        # Beklemede
    PROCESSING = "processing"  # İşleniyor
    COMPLETED = "completed"    # Tamamlandı
    FAILED = "failed"          # Başarısız
    CANCELLED = "cancelled"    # İptal edildi
    REFUNDED = "refunded"      # İade edildi


class PaymentMethod(str, Enum):
    """Ödeme yöntemi - Kullanılan ödeme kanalı"""
    MONERO = "monero"    # Monero (XMR) - Anonim kripto para
    BTCPAY = "btcpay"    # BTCPay Server (BTC, Lightning)
    WALLET = "wallet"    # İç bakiye - Platform cüzdanı


class WithdrawalStatus(str, Enum):
    """Para çekme durumu - Çekme talebinin şu anki hali"""
    PENDING = "pending"        # Beklemede - Onay bekliyor
    APPROVED = "approved"      # Onaylandı - İşlenecek
    PROCESSING = "processing"  # İşleniyor - Blockchain'e gönderiliyor
    COMPLETED = "completed"    # Tamamlandı - Para gönderildi
    REJECTED = "rejected"      # Reddedildi
    CANCELLED = "cancelled"    # İptal edildi


class Wallet(Base):
    """
    Kullanıcı Cüzdan Modeli
    =======================
    Her kullanıcının bir cüzdanı vardır. Bakiye, bekleyen bakiye ve
    toplam kazanç/harcama istatistiklerini tutar.
    """
    __tablename__ = "wallets"
    
    # Cüzdanın sahibi
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    # Bakiyeler
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)          # Kullanılabilir bakiye
    pending_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # Bekleyen bakiye (onay bekliyor)
    
    # İstatistikler
    total_earned: Mapped[float] = mapped_column(Numeric(12, 2), default=0)     # Toplam kazanılan
    total_withdrawn: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # Toplam çekilen
    total_spent: Mapped[float] = mapped_column(Numeric(12, 2), default=0)      # Toplam harcanan
    
    # İlişkiler
    user: Mapped["User"] = relationship("User", back_populates="wallet")
    
    def __repr__(self):
        return f"<Wallet {self.user_id} balance={self.balance}>"


class Transaction(Base):
    """
    Finansal İşlem Modeli
    =====================
    Platformdaki tüm para hareketlerini kaydeder.
    Abonelikler, bahşişler, PPV satışları, para çekimler vb.
    Kripto para detayları (tutar, kur, tx hash) da burada saklanır.
    """
    __tablename__ = "transactions"
    
    # Taraflar - Kim yaptı, kime yapıldı
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recipient_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # İşlem detayları
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)    # İşlem türü
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)  # Durum
    
    # Tutarlar
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)      # Brüt tutar
    fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)              # Platform komisyonu
    net_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)  # Net tutar (komisyon düşülmüş)
    currency: Mapped[str] = mapped_column(String(10), default="USD")           # Para birimi
    
    # Kripto para detayları
    crypto_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))     # Kripto miktarı
    crypto_currency: Mapped[Optional[str]] = mapped_column(String(10))         # Kripto para birimi (XMR, BTC, vb.)
    exchange_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))     # İşlem anındaki kur
    
    # Ödeme bilgileri
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod))  # Ödeme yöntemi
    payment_id: Mapped[Optional[str]] = mapped_column(String(255))             # Harici ödeme ID'si
    
    # İlişkili öğeler
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("subscriptions.id"))
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id"))
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id"))
    stream_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("streams.id"))
    
    # Notlar ve ek bilgiler
    description: Mapped[Optional[str]] = mapped_column(String(255))  # Açıklama
    tx_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)       # Ek meta veriler (metadata is reserved)
    
    # İlişkiler
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])         # İşlemi yapan
    recipient: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recipient_id])  # Alıcı (varsa)
    
    # Veritabanı indexleri - Sorgu performansı için
    __table_args__ = (
        Index('idx_transactions_user_id', 'user_id'),          # Kullanıcı işlemleri için
        Index('idx_transactions_recipient_id', 'recipient_id'), # Alıcı bazlı sorgular için
        Index('idx_transactions_type', 'type'),                 # İşlem tipi filtrelemesi
        Index('idx_transactions_status', 'status'),             # Durum filtrelemesi
        Index('idx_transactions_created_at', 'created_at'),     # Tarih sıralaması
        Index('idx_transactions_payment_id', 'payment_id'),     # Ödeme ID aramaları
    )
    
    def __repr__(self):
        return f"<Transaction {self.id} {self.type} {self.amount}>"


class Withdrawal(Base):
    """
    Para Çekme Talebi Modeli
    ========================
    İçerik üreticilerinin kazançlarını kripto para olarak çekmesi için
    oluşturdukları talepler. Admin onayı gerektirir.
    """
    __tablename__ = "withdrawals"
    
    # Talebi oluşturan kullanıcı
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Tutarlar
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)      # Talep edilen tutar
    fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)              # İşlem ücreti
    net_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)  # Net gönderilecek tutar
    
    # Kripto ödeme bilgileri
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)  # Hangi kripto
    payout_address: Mapped[str] = mapped_column(String(200), nullable=False)   # Cüzdan adresi
    
    # Blockchain işlem detayları
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255))               # İşlem hash'i
    crypto_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))    # Gönderilen kripto miktarı
    exchange_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))    # Çevirme kuru
    
    # Durum
    status: Mapped[WithdrawalStatus] = mapped_column(SQLEnum(WithdrawalStatus), default=WithdrawalStatus.PENDING)
    
    # Admin inceleme bilgileri
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))  # İnceleyen admin
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # İnceleme tarihi
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)  # Red gerekçesi (varsa)
    
    # İşleme bilgileri
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # Gönderim tarihi
    
    # İlişkiler
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])              # Talep sahibi
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by_id])  # İnceleyen admin
    
    # Veritabanı indexleri - Sorgu performansı için
    __table_args__ = (
        Index('idx_withdrawals_user_id', 'user_id'),      # Kullanıcı çekimleri için
        Index('idx_withdrawals_status', 'status'),        # Durum filtrelemesi
        Index('idx_withdrawals_created_at', 'created_at'), # Tarih sıralaması
    )

