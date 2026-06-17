"""
Admin schemas
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.user import UserRole, UserStatus
from app.models.admin import ReportStatus, ReportType
from app.models.transaction import WithdrawalStatus, PaymentMethod


class AdminUserResponse(BaseModel):
    id: UUID
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_creator: bool
    is_verified_creator: bool = False
    is_email_verified: bool
    subscribers_count: int = 0
    posts_count: int = 0
    created_at: datetime
    last_login_at: Optional[datetime] = None
    banned_at: Optional[datetime] = None
    ban_reason: Optional[str] = None
    
    # Additional stats (populated separately)
    wallet_balance: Optional[float] = None
    total_earned: Optional[float] = None
    total_spent: Optional[float] = None
    
    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_verified_creator: Optional[bool] = None
    is_email_verified: Optional[bool] = None
    is_creator: Optional[bool] = None


class AdminStatsResponse(BaseModel):
    total_users: int
    new_users: int
    total_creators: int
    total_revenue: float
    total_transactions: float
    pending_withdrawals: int
    pending_withdrawal_amount: float
    total_posts: int
    active_subscriptions: int
    pending_reports: int
    period: str


class ReportResponse(BaseModel):
    id: UUID
    reporter_id: UUID
    reported_user_id: Optional[UUID] = None
    type: ReportType
    reason: Optional[str] = None
    description: Optional[str] = None
    reported_type: Optional[str] = None
    reported_id: Optional[UUID] = None
    status: ReportStatus
    resolution_note: Optional[str] = None
    reviewed_by_id: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportUpdate(BaseModel):
    status: ReportStatus
    admin_notes: Optional[str] = None


class WithdrawalAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    fee: float
    net_amount: float
    crypto_amount: Optional[float] = None
    crypto_currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    payment_method: PaymentMethod
    payout_address: str
    status: WithdrawalStatus
    tx_hash: Optional[str] = None
    rejection_reason: Optional[str] = None
    reviewed_by_id: Optional[UUID] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    
    # User info (populated separately)
    username: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class WithdrawalAdminUpdate(BaseModel):
    status: WithdrawalStatus
    rejection_reason: Optional[str] = None


class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=5000)
    type: str = "info"  # info, warning, success, error
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class AnnouncementResponse(BaseModel):
    id: UUID
    title: str
    content: str
    type: str = "info"
    is_active: bool
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class SiteSettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    platform_fee_percent: Optional[Decimal] = None
    withdrawal_fee_percent: Optional[Decimal] = None
    min_withdrawal_amount: Optional[Decimal] = None
    min_subscription_price: Optional[Decimal] = None
    max_subscription_price: Optional[Decimal] = None
    maintenance_mode: Optional[bool] = None
    registration_enabled: Optional[bool] = None
    creator_verification_required: Optional[bool] = None
    monero_enabled: Optional[bool] = None
    btcpay_enabled: Optional[bool] = None
