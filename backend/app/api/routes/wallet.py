"""
Withdrawal and payout API routes
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.transaction import (
    Transaction, 
    TransactionType, 
    TransactionStatus, 
    PaymentMethod,
    Wallet,
    Withdrawal,
    WithdrawalStatus,
)
from app.schemas.transaction import (
    WithdrawalCreate,
    WithdrawalResponse,
    TransactionResponse,
    WalletResponse,
    EarningsStats,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.api.deps import get_current_user
from app.services.monero import monero_service
from app.services.btcpay import btcpay_service

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's wallet"""
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        wallet = Wallet(user_id=current_user.id)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    
    return WalletResponse(
        balance=float(wallet.balance),
        pending_balance=float(wallet.pending_balance),
        total_earned=float(wallet.total_earned),
        total_withdrawn=float(wallet.total_withdrawn),
        total_spent=float(wallet.total_spent),
    )


@router.get("/transactions", response_model=PaginatedResponse)
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_filter: Optional[TransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's transaction history"""
    query = select(Transaction).where(
        (Transaction.user_id == current_user.id) | 
        (Transaction.recipient_id == current_user.id)
    )
    
    if type_filter:
        query = query.where(Transaction.type == type_filter)
    
    if start_date:
        query = query.where(Transaction.created_at >= start_date)
    
    if end_date:
        query = query.where(Transaction.created_at <= end_date)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Transaction.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return PaginatedResponse(
        items=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.get("/earnings/stats", response_model=EarningsStats)
async def get_earnings_stats(
    period: str = Query("month", regex="^(day|week|month|year|all)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get earnings statistics"""
    now = datetime.utcnow()
    
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    base_query = select(Transaction).where(
        and_(
            Transaction.recipient_id == current_user.id,
            Transaction.status == TransactionStatus.COMPLETED
        )
    )
    
    if start_date:
        base_query = base_query.where(Transaction.created_at >= start_date)
    
    # Total earnings
    result = await db.execute(
        select(func.sum(Transaction.net_amount))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    total_earnings = float(result.scalar() or 0)
    
    # Subscriptions earnings
    result = await db.execute(
        select(func.sum(Transaction.net_amount))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.type == TransactionType.SUBSCRIPTION,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    subscription_earnings = float(result.scalar() or 0)
    
    # Tips earnings
    result = await db.execute(
        select(func.sum(Transaction.net_amount))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.type == TransactionType.TIP,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    tips_earnings = float(result.scalar() or 0)
    
    # Post unlocks earnings
    result = await db.execute(
        select(func.sum(Transaction.net_amount))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.type == TransactionType.POST_UNLOCK,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    post_unlock_earnings = float(result.scalar() or 0)
    
    # Message earnings
    result = await db.execute(
        select(func.sum(Transaction.net_amount))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.type == TransactionType.MESSAGE,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    message_earnings = float(result.scalar() or 0)
    
    # Transaction count
    result = await db.execute(
        select(func.count(Transaction.id))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    transaction_count = result.scalar() or 0
    
    # Platform fees paid
    result = await db.execute(
        select(func.sum(Transaction.fee))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    platform_fees = float(result.scalar() or 0)
    
    return EarningsStats(
        total=total_earnings,
        subscriptions=subscription_earnings,
        tips=tips_earnings,
        post_unlocks=post_unlock_earnings,
        messages=message_earnings,
        referrals=0,  # TODO: Implement referral earnings
        transaction_count=transaction_count,
        platform_fees=platform_fees,
        period=period,
    )


# ============ WITHDRAWALS ============

@router.post("/withdraw", response_model=WithdrawalResponse)
async def request_withdrawal(
    data: WithdrawalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request a withdrawal"""
    # Get wallet
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cüzdan bulunamadı"
        )
    
    # Check minimum withdrawal
    min_withdrawal = settings.min_withdrawal_amount
    if data.amount < min_withdrawal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum çekim tutarı ${min_withdrawal}"
        )
    
    # Check balance
    if wallet.balance < data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yetersiz bakiye"
        )
    
    # Check pending withdrawals
    result = await db.execute(
        select(func.count(Withdrawal.id))
        .where(
            and_(
                Withdrawal.user_id == current_user.id,
                Withdrawal.status == WithdrawalStatus.PENDING
            )
        )
    )
    pending_count = result.scalar() or 0
    
    if pending_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten bekleyen bir çekim isteğiniz var"
        )
    
    # Calculate withdrawal fee
    withdrawal_fee = data.amount * (settings.withdrawal_fee_percent / 100)
    net_amount = data.amount - withdrawal_fee
    
    # Calculate crypto amount
    if data.payment_method == PaymentMethod.MONERO:
        crypto_amount, exchange_rate = await monero_service.calculate_xmr_amount(net_amount)
        crypto_currency = "XMR"
    elif data.payment_method == PaymentMethod.BTCPAY:
        crypto_amount, exchange_rate = await btcpay_service.calculate_btc_amount(net_amount)
        crypto_currency = "BTC"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz ödeme yöntemi"
        )

    # Create withdrawal request (Withdrawal modelinde crypto_currency alanı yoktur)
    withdrawal = Withdrawal(
        user_id=current_user.id,
        amount=data.amount,
        fee=withdrawal_fee,
        net_amount=net_amount,
        payment_method=data.payment_method,
        payout_address=data.payout_address,
        crypto_amount=crypto_amount,
        exchange_rate=exchange_rate,
        status=WithdrawalStatus.PENDING,
    )
    
    # Deduct from wallet (hold in pending)
    wallet.balance -= data.amount
    wallet.pending_balance += data.amount
    
    db.add(withdrawal)
    await db.commit()
    await db.refresh(withdrawal)

    return WithdrawalResponse.model_validate(withdrawal)


@router.get("/withdrawals", response_model=PaginatedResponse)
async def get_withdrawals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[WithdrawalStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's withdrawal history"""
    query = select(Withdrawal).where(Withdrawal.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Withdrawal.status == status_filter)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Withdrawal.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    withdrawals = result.scalars().all()
    
    return PaginatedResponse(
        items=[WithdrawalResponse.model_validate(w) for w in withdrawals],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.delete("/withdrawals/{withdrawal_id}", response_model=SuccessResponse)
async def cancel_withdrawal(
    withdrawal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending withdrawal"""
    result = await db.execute(
        select(Withdrawal)
        .where(
            and_(
                Withdrawal.id == withdrawal_id,
                Withdrawal.user_id == current_user.id
            )
        )
    )
    withdrawal = result.scalar_one_or_none()
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Çekim isteği bulunamadı"
        )
    
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece bekleyen çekim istekleri iptal edilebilir"
        )
    
    # Return funds to wallet
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()
    
    if wallet:
        wallet.balance += withdrawal.amount
        wallet.pending_balance -= withdrawal.amount
    
    withdrawal.status = WithdrawalStatus.CANCELLED
    
    await db.commit()
    
    return SuccessResponse(message="Çekim isteği iptal edildi")


@router.get("/payout-info")
async def get_payout_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payout configuration info"""
    # Get current exchange rates
    xmr_rate = await monero_service.get_exchange_rate()
    btc_rate = await btcpay_service.get_exchange_rate()
    
    return {
        "min_withdrawal": settings.min_withdrawal_amount,
        "withdrawal_fee_percent": settings.withdrawal_fee_percent,
        "payment_methods": [
            {
                "id": "monero",
                "name": "Monero (XMR)",
                "currency": "XMR",
                "exchange_rate": xmr_rate,
                "min_amount": 10,  # $10 minimum for XMR
                "icon": "monero",
            },
            {
                "id": "btcpay",
                "name": "Bitcoin (BTC)",
                "currency": "BTC",
                "exchange_rate": btc_rate,
                "min_amount": 50,  # $50 minimum for BTC
                "icon": "bitcoin",
            }
        ],
        "estimated_processing_time": "24-48 hours",
        "notes": [
            "Çekimler genellikle 24-48 saat içinde işlenir",
            "Kripto para fiyat dalgalanmaları nedeniyle tutar değişebilir",
            "Doğru adres girdiğinizden emin olun, yanlış transferler geri alınamaz",
        ]
    }


@router.post("/save-payout-address", response_model=SuccessResponse)
async def save_payout_address(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save preferred payout address (kullanıcı ayarlarında saklanır)"""
    from app.models.user import UserSettings

    address_type = data.get("type")  # "monero" or "bitcoin"
    address = data.get("address")

    if not address_type or not address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Adres tipi ve adres gerekli"
        )

    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.add(user_settings)

    if address_type == "monero":
        user_settings.monero_address = address
    elif address_type == "bitcoin":
        user_settings.btc_address = address
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz adres tipi"
        )

    await db.commit()

    return SuccessResponse(message="Ödeme adresi kaydedildi")
