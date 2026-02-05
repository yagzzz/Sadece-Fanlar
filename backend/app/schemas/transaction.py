"""
Transaction and wallet schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    SUBSCRIPTION = "subscription"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    TIP = "tip"
    CHAT_TIP = "chat_tip"
    POST_UNLOCK = "post_unlock"
    MESSAGE_UNLOCK = "message_unlock"
    STREAM_ACCESS = "stream_access"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"
    REFERRAL_BONUS = "referral_bonus"
    PLATFORM_FEE = "platform_fee"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    MONERO = "monero"
    BTCPAY = "btcpay"
    WALLET = "wallet"


class WalletResponse(BaseModel):
    """Wallet response"""
    balance: float
    pending_balance: float
    total_earned: float
    total_withdrawn: float
    total_spent: float
    
    # Stats this month
    earnings_this_month: float = 0
    
    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: UUID
    
    type: TransactionType
    status: TransactionStatus
    
    amount: float
    fee: float
    net_amount: float
    currency: str
    
    crypto_amount: Optional[float]
    crypto_currency: Optional[str]
    
    payment_method: PaymentMethod
    payment_id: Optional[str]
    
    # Related user (sender or recipient)
    other_user_id: Optional[UUID]
    other_user_username: Optional[str]
    other_user_avatar: Optional[str]
    
    description: Optional[str]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class DepositCreate(BaseModel):
    """Create a deposit request"""
    amount: float = Field(..., ge=5, le=10000, description="Yatırılacak tutar (USD)")
    payment_method: PaymentMethod = Field(..., description="Ödeme yöntemi")


class WithdrawalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


class WithdrawalCreate(BaseModel):
    """Create a withdrawal request"""
    amount: float = Field(..., ge=50, le=10000, description="Çekilecek tutar (USD)")
    payment_method: PaymentMethod = Field(..., description="Ödeme yöntemi")
    payout_address: str = Field(..., min_length=20, max_length=200, description="Kripto cüzdan adresi")


class WithdrawalResponse(BaseModel):
    """Withdrawal response"""
    id: UUID
    
    amount: float
    fee: float
    net_amount: float
    
    payment_method: PaymentMethod
    payout_address: str
    
    tx_hash: Optional[str]
    crypto_amount: Optional[float]
    exchange_rate: Optional[float]
    
    status: WithdrawalStatus
    rejection_reason: Optional[str]
    
    created_at: datetime
    reviewed_at: Optional[datetime]
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EarningsStats(BaseModel):
    """Earnings statistics"""
    total_earnings: float
    earnings_this_month: float
    earnings_last_month: float
    
    subscriptions_revenue: float
    tips_revenue: float
    ppv_revenue: float
    stream_revenue: float
    
    pending_balance: float
    available_balance: float
    
    total_subscribers: int
    new_subscribers_this_month: int
    
    # Chart data
    daily_earnings: list = []  # Last 30 days
