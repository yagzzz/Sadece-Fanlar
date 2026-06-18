"""
Subscription API routes
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.subscription import (
    Subscription, 
    SubscriptionStatus, 
    SubscriptionType,
    SubscriptionPlan,
    SubscriptionBundle
)
from app.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentMethod, Wallet
from app.models.payment import PaymentRequest, PaymentRequestStatus, PaymentRequestType
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    SubscriptionBundleCreate,
    SubscriptionBundleResponse,
    SubscriberStats,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.api.deps import get_current_user
from app.services.monero import monero_service
from app.services.btcpay import btcpay_service

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ============ SUBSCRIPTION PLANS ============

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_my_subscription_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get creator's subscription plans"""
    result = await db.execute(
        select(SubscriptionPlan)
        .where(
            and_(
                SubscriptionPlan.creator_id == current_user.id,
                SubscriptionPlan.is_active == True
            )
        )
        .order_by(SubscriptionPlan.price)
    )
    plans = result.scalars().all()
    return plans


@router.get("/users/{username}/plans", response_model=List[SubscriptionPlanResponse])
async def get_user_subscription_plans(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a creator's available subscription plans"""
    result = await db.execute(select(User).where(User.username == username))
    creator = result.scalar_one_or_none()
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    result = await db.execute(
        select(SubscriptionPlan)
        .where(
            and_(
                SubscriptionPlan.creator_id == creator.id,
                SubscriptionPlan.is_active == True,
                SubscriptionPlan.is_public == True
            )
        )
        .order_by(SubscriptionPlan.price)
    )
    plans = result.scalars().all()
    return plans


@router.post("/plans", response_model=SubscriptionPlanResponse)
async def create_subscription_plan(
    data: SubscriptionPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription plan"""
    # Check plan limit
    result = await db.execute(
        select(func.count(SubscriptionPlan.id))
        .where(SubscriptionPlan.creator_id == current_user.id)
    )
    plan_count = result.scalar()
    
    if plan_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="En fazla 5 abonelik planı oluşturabilirsiniz"
        )
    
    plan = SubscriptionPlan(
        creator_id=current_user.id,
        name=data.name,
        description=data.description,
        price=data.price,
        currency=data.currency,
        duration_months=data.duration_months,
        tier=data.tier,
        is_public=data.is_public,
    )
    
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    
    return plan


@router.put("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: UUID,
    data: SubscriptionPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a subscription plan"""
    result = await db.execute(
        select(SubscriptionPlan)
        .where(
            and_(
                SubscriptionPlan.id == plan_id,
                SubscriptionPlan.creator_id == current_user.id
            )
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan bulunamadı"
        )
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    
    await db.commit()
    await db.refresh(plan)
    
    return plan


@router.delete("/plans/{plan_id}", response_model=SuccessResponse)
async def delete_subscription_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete (deactivate) a subscription plan"""
    result = await db.execute(
        select(SubscriptionPlan)
        .where(
            and_(
                SubscriptionPlan.id == plan_id,
                SubscriptionPlan.creator_id == current_user.id
            )
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan bulunamadı"
        )
    
    # Don't actually delete, just deactivate
    plan.is_active = False
    await db.commit()
    
    return SuccessResponse(message="Plan silindi")


# ============ SUBSCRIPTION BUNDLES ============

@router.get("/bundles", response_model=List[SubscriptionBundleResponse])
async def get_my_subscription_bundles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get creator's subscription bundles"""
    result = await db.execute(
        select(SubscriptionBundle)
        .where(
            and_(
                SubscriptionBundle.creator_id == current_user.id,
                SubscriptionBundle.is_active == True
            )
        )
    )
    bundles = result.scalars().all()
    return bundles


@router.post("/bundles", response_model=SubscriptionBundleResponse)
async def create_subscription_bundle(
    data: SubscriptionBundleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a subscription bundle"""
    bundle = SubscriptionBundle(
        creator_id=current_user.id,
        name=data.name,
        description=data.description,
        price=data.price,
        original_price=data.original_price,
        currency=data.currency,
        duration_months=data.duration_months,
        max_purchases=data.max_purchases,
        expires_at=data.expires_at,
    )
    
    db.add(bundle)
    await db.commit()
    await db.refresh(bundle)
    
    return bundle


# ============ SUBSCRIPTIONS ============

@router.post("/subscribe/{username}")
async def subscribe_to_user(
    username: str,
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to a creator"""
    # Get creator
    result = await db.execute(select(User).where(User.username == username))
    creator = result.scalar_one_or_none()
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    if creator.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinize abone olamazsınız"
        )
    
    # Check if already subscribed
    result = await db.execute(
        select(Subscription)
        .where(
            and_(
                Subscription.subscriber_id == current_user.id,
                Subscription.creator_id == creator.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcıya zaten abonesiniz"
        )

    # Süreyi abonelik türünden hesapla
    months_map = {"1_month": 1, "3_months": 3, "6_months": 6, "12_months": 12}
    type_value = data.type.value if hasattr(data.type, "value") else str(data.type)
    months = months_map.get(type_value, 1)

    # Fiyatlandırma (içerik üreticisinin çok-aylık özel fiyatları varsa onları kullan)
    base_price = float(creator.subscription_price) if creator.subscription_price else 0.0
    if months == 3 and creator.subscription_price_3m:
        total_price = float(creator.subscription_price_3m)
    elif months == 6 and creator.subscription_price_6m:
        total_price = float(creator.subscription_price_6m)
    elif months == 12 and creator.subscription_price_12m:
        total_price = float(creator.subscription_price_12m)
    else:
        total_price = base_price * months

    far_future = datetime.utcnow() + timedelta(days=365 * 100)

    # Ücretsiz/fiyatsız abonelik
    if total_price <= 0:
        subscription = Subscription(
            subscriber_id=current_user.id,
            creator_id=creator.id,
            type=SubscriptionType.FREE,
            status=SubscriptionStatus.ACTIVE,
            amount=0,
            payment_method="free",
            starts_at=datetime.utcnow(),
            expires_at=far_future,
        )
        db.add(subscription)
        creator.subscribers_count = (creator.subscribers_count or 0) + 1
        current_user.subscriptions_count = (current_user.subscriptions_count or 0) + 1
        await db.commit()
        await db.refresh(subscription)
        return SubscriptionResponse.model_validate(subscription)

    # Cüzdandan ödeme (anında)
    if data.payment_method == "wallet":
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == current_user.id)
        )
        wallet = result.scalar_one_or_none()

        if not wallet or wallet.balance < total_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yetersiz bakiye"
            )

        from app.services.site_settings import get_fee_percent
        fee_percent = await get_fee_percent(db)
        platform_fee = total_price * (fee_percent / 100)
        net_amount = total_price - platform_fee

        wallet.balance -= total_price
        wallet.total_spent += total_price

        result = await db.execute(
            select(Wallet).where(Wallet.user_id == creator.id)
        )
        creator_wallet = result.scalar_one_or_none()
        if creator_wallet:
            creator_wallet.balance += net_amount
            creator_wallet.total_earned += net_amount

        subscription = Subscription(
            subscriber_id=current_user.id,
            creator_id=creator.id,
            type=SubscriptionType.PAID,
            status=SubscriptionStatus.ACTIVE,
            amount=total_price,
            payment_method="wallet",
            starts_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30 * months),
        )
        db.add(subscription)

        transaction = Transaction(
            user_id=current_user.id,
            recipient_id=creator.id,
            type=TransactionType.SUBSCRIPTION,
            status=TransactionStatus.COMPLETED,
            amount=total_price,
            fee=platform_fee,
            net_amount=net_amount,
            payment_method=PaymentMethod.WALLET,
            description=f"{months} aylık abonelik",
        )
        db.add(transaction)

        creator.subscribers_count = (creator.subscribers_count or 0) + 1
        current_user.subscriptions_count = (current_user.subscriptions_count or 0) + 1

        await db.commit()
        await db.refresh(subscription)
        return SubscriptionResponse.model_validate(subscription)

    # Kripto ödeme isteği (Monero / BTCPay) - tamamlanınca abonelik aktifleşir
    if data.payment_method == "monero":
        crypto_amount, exchange_rate = await monero_service.calculate_xmr_amount(total_price)
        integrated_address, payment_id = await monero_service.create_integrated_address()

        payment_request = PaymentRequest(
            user_id=current_user.id,
            type=PaymentRequestType.SUBSCRIPTION,
            status=PaymentRequestStatus.AWAITING_PAYMENT,
            amount_usd=total_price,
            amount_crypto=crypto_amount,
            crypto_currency="XMR",
            exchange_rate=exchange_rate,
            payment_method=PaymentMethod.MONERO,
            monero_address=await monero_service.get_address(),
            monero_payment_id=payment_id,
            monero_integrated_address=integrated_address,
            recipient_id=creator.id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            payment_metadata={"months": months},
        )

    elif data.payment_method == "btcpay":
        invoice = await btcpay_service.create_invoice(
            amount=total_price,
            currency="USD",
            order_id=f"sub_{current_user.id}_{creator.id}_{datetime.utcnow().timestamp()}",
            metadata={
                "user_id": str(current_user.id),
                "creator_id": str(creator.id),
                "type": "subscription",
                "months": months,
            },
        )

        crypto_amount, exchange_rate = await btcpay_service.calculate_btc_amount(total_price)

        payment_request = PaymentRequest(
            user_id=current_user.id,
            type=PaymentRequestType.SUBSCRIPTION,
            status=PaymentRequestStatus.AWAITING_PAYMENT,
            amount_usd=total_price,
            amount_crypto=crypto_amount,
            crypto_currency="BTC",
            exchange_rate=exchange_rate,
            payment_method=PaymentMethod.BTCPAY,
            btcpay_invoice_id=invoice["id"],
            btcpay_checkout_url=invoice.get("checkoutLink"),
            recipient_id=creator.id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            payment_metadata={"months": months},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz ödeme yöntemi"
        )

    db.add(payment_request)
    await db.commit()
    await db.refresh(payment_request)

    return {
        "payment_required": True,
        "payment_request": {
            "id": str(payment_request.id),
            "amount_usd": float(payment_request.amount_usd),
            "amount_crypto": float(payment_request.amount_crypto) if payment_request.amount_crypto else None,
            "crypto_currency": payment_request.crypto_currency,
            "monero_integrated_address": payment_request.monero_integrated_address,
            "btcpay_checkout_url": payment_request.btcpay_checkout_url,
            "expires_at": payment_request.expires_at.isoformat(),
        }
    }


@router.delete("/unsubscribe/{username}", response_model=SuccessResponse)
async def unsubscribe_from_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel subscription to a creator"""
    result = await db.execute(select(User).where(User.username == username))
    creator = result.scalar_one_or_none()
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    result = await db.execute(
        select(Subscription)
        .where(
            and_(
                Subscription.subscriber_id == current_user.id,
                Subscription.creator_id == creator.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif abonelik bulunamadı"
        )
    
    # Mark as cancelled but keep active until expiry
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    subscription.auto_renew = False
    
    await db.commit()
    
    return SuccessResponse(message="Abonelik iptal edildi. Süre sonuna kadar aktif kalacak.")


@router.get("/my/subscriptions", response_model=PaginatedResponse)
async def get_my_subscriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[SubscriptionStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's active subscriptions (creators they follow)"""
    query = select(Subscription).where(Subscription.subscriber_id == current_user.id)
    
    if status_filter:
        query = query.where(Subscription.status == status_filter)
    else:
        query = query.where(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELLED])
        )
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Subscription.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return PaginatedResponse(
        items=[SubscriptionResponse.model_validate(s) for s in subscriptions],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.get("/my/subscribers", response_model=PaginatedResponse)
async def get_my_subscribers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[SubscriptionStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get creator's subscribers"""
    query = select(Subscription).where(Subscription.creator_id == current_user.id)
    
    if status_filter:
        query = query.where(Subscription.status == status_filter)
    else:
        query = query.where(Subscription.status == SubscriptionStatus.ACTIVE)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Subscription.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return PaginatedResponse(
        items=[SubscriptionResponse.model_validate(s) for s in subscriptions],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.get("/my/subscribers/stats", response_model=SubscriberStats)
async def get_subscriber_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscriber statistics for creator"""
    # Active subscribers
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(
            and_(
                Subscription.creator_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    active_count = result.scalar() or 0
    
    # New subscribers this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(
            and_(
                Subscription.creator_id == current_user.id,
                Subscription.created_at >= month_start
            )
        )
    )
    new_this_month = result.scalar() or 0
    
    # Expired this month
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(
            and_(
                Subscription.creator_id == current_user.id,
                Subscription.status == SubscriptionStatus.EXPIRED,
                Subscription.expires_at >= month_start
            )
        )
    )
    expired_this_month = result.scalar() or 0
    
    # Total earnings from subscriptions
    result = await db.execute(
        select(func.sum(Transaction.net_amount))
        .where(
            and_(
                Transaction.recipient_id == current_user.id,
                Transaction.type == TransactionType.SUBSCRIPTION,
                Transaction.status == TransactionStatus.COMPLETED
            )
        )
    )
    total_earnings = float(result.scalar() or 0)
    
    return SubscriberStats(
        total_subscribers=active_count,
        active_subscribers=active_count,
        new_this_month=new_this_month,
        churned_this_month=expired_this_month,
        monthly_revenue=0.0,
        lifetime_revenue=total_earnings,
    )


@router.get("/check/{username}")
async def check_subscription(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if current user is subscribed to a creator"""
    result = await db.execute(select(User).where(User.username == username))
    creator = result.scalar_one_or_none()
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    result = await db.execute(
        select(Subscription)
        .where(
            and_(
                Subscription.subscriber_id == current_user.id,
                Subscription.creator_id == creator.id,
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELLED])
            )
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        return {"subscribed": False}
    
    # Check if still valid
    if subscription.expires_at and subscription.expires_at < datetime.utcnow():
        subscription.status = SubscriptionStatus.EXPIRED
        await db.commit()
        return {"subscribed": False, "expired": True}
    
    return {
        "subscribed": True,
        "subscription": SubscriptionResponse.model_validate(subscription),
        "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
        "auto_renew": subscription.auto_renew,
    }
