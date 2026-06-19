"""
Admin Panel API routes
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.models.post import Post, PostStatus
from app.models.subscription import Subscription
from app.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentMethod, Wallet, Withdrawal, WithdrawalStatus
from app.models.admin import (
    AdminLog,
    AdminAction,
    Report,
    ReportStatus,
    ReportType,
    SiteSettings,
    Announcement,
)
from app.schemas.admin import (
    AdminUserResponse,
    AdminUserUpdate,
    AdminStatsResponse,
    ReportResponse,
    ReportUpdate,
    WithdrawalAdminResponse,
    WithdrawalAdminUpdate,
    AnnouncementCreate,
    AnnouncementResponse,
    SiteSettingsUpdate,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.api.deps import get_current_user, get_admin_user
from app.services.monero import monero_service
from app.services.btcpay import btcpay_service
from app.services.site_settings import get_platform_settings, update_platform_settings
from app.services import wallet_service

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============ ADMIN MIDDLEWARE ============

def _json_safe(details: Optional[dict]) -> Optional[dict]:
    """UUID/datetime gibi değerleri JSONB için string'e çevirir."""
    if not details:
        return None
    safe = {}
    for key, value in details.items():
        if isinstance(value, (UUID, datetime)):
            safe[key] = str(value)
        else:
            safe[key] = value
    return safe


async def log_admin_action(
    db: AsyncSession,
    admin_id: UUID,
    action: AdminAction,
    target_type: str,
    target_id: Optional[UUID] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
):
    """
    Yönetici işlemini kaydeder.
    GİZLİLİK: IP adresi saklanmaz (anonimlik). AdminLog modeline uygun
    şekilde `description` ve `data` alanları kullanılır.
    """
    log = AdminLog(
        admin_id=admin_id,
        action=action,
        description=f"{action.value} -> {target_type}" + (f":{target_id}" if target_id else ""),
        target_type=target_type,
        target_id=target_id,
        data=_json_safe(details),
    )
    db.add(log)
    await db.commit()


# ============ DASHBOARD ============

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    period: str = Query("month", regex="^(day|week|month|year|all)$"),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
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
    
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    
    # New users in period
    if start_date:
        result = await db.execute(
            select(func.count(User.id))
            .where(User.created_at >= start_date)
        )
        new_users = result.scalar() or 0
    else:
        new_users = total_users
    
    # Active creators
    result = await db.execute(
        select(func.count(User.id))
        .where(User.is_creator == True)
    )
    total_creators = result.scalar() or 0
    
    # Total revenue (platform fees)
    result = await db.execute(
        select(func.sum(Transaction.fee))
        .where(
            and_(
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    total_revenue = float(result.scalar() or 0)
    
    # Total transactions value
    result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(
            and_(
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= start_date if start_date else True
            )
        )
    )
    total_transactions = float(result.scalar() or 0)
    
    # Pending withdrawals
    result = await db.execute(
        select(func.count(Withdrawal.id))
        .where(Withdrawal.status == WithdrawalStatus.PENDING)
    )
    pending_withdrawals = result.scalar() or 0
    
    # Pending withdrawals amount
    result = await db.execute(
        select(func.sum(Withdrawal.amount))
        .where(Withdrawal.status == WithdrawalStatus.PENDING)
    )
    pending_withdrawal_amount = float(result.scalar() or 0)
    
    # Total posts
    result = await db.execute(select(func.count(Post.id)))
    total_posts = result.scalar() or 0
    
    # Active subscriptions
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(Subscription.status == "active")
    )
    active_subscriptions = result.scalar() or 0
    
    # Pending reports
    result = await db.execute(
        select(func.count(Report.id))
        .where(Report.status == ReportStatus.PENDING)
    )
    pending_reports = result.scalar() or 0
    
    return AdminStatsResponse(
        total_users=total_users,
        new_users=new_users,
        total_creators=total_creators,
        total_revenue=total_revenue,
        total_transactions=total_transactions,
        pending_withdrawals=pending_withdrawals,
        pending_withdrawal_amount=pending_withdrawal_amount,
        total_posts=total_posts,
        active_subscriptions=active_subscriptions,
        pending_reports=pending_reports,
        period=period,
    )


# ============ USER MANAGEMENT ============

@router.get("/users", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status_filter: Optional[UserStatus] = None,
    is_creator: Optional[bool] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with filters"""
    query = select(User)
    
    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.where(User.role == role)
    
    if status_filter:
        query = query.where(User.status == status_filter)
    
    if is_creator is not None:
        query = query.where(User.is_creator == is_creator)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return PaginatedResponse(
        items=[AdminUserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: UUID,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user details"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Get additional stats
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    wallet = result.scalar_one_or_none()
    
    response = AdminUserResponse.model_validate(user)
    if wallet:
        response.wallet_balance = float(wallet.balance)
        response.total_earned = float(wallet.total_earned)
        response.total_spent = float(wallet.total_spent)
    
    return response


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin actions)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Prevent self-demotion
    if user_id == admin.id and data.role and data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendi rolünüzü düşüremezsiniz"
        )
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.UPDATE_USER,
        target_type="user",
        target_id=user_id,
        details=data.model_dump(exclude_unset=True),
    )
    
    return AdminUserResponse.model_validate(user)


@router.post("/users/{user_id}/ban", response_model=SuccessResponse)
async def ban_user(
    user_id: UUID,
    reason: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Ban a user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinizi banlayamazsınız"
        )
    
    user.status = UserStatus.BANNED
    user.banned_at = datetime.utcnow()
    user.ban_reason = reason
    
    await db.commit()
    
    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.BAN_USER,
        target_type="user",
        target_id=user_id,
        details={"reason": reason},
    )
    
    return SuccessResponse(message="Kullanıcı banlandı")


@router.post("/users/{user_id}/unban", response_model=SuccessResponse)
async def unban_user(
    user_id: UUID,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Unban a user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    user.status = UserStatus.ACTIVE
    user.banned_at = None
    user.ban_reason = None
    
    await db.commit()
    
    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.UNBAN_USER,
        target_type="user",
        target_id=user_id,
    )
    
    return SuccessResponse(message="Kullanıcı banı kaldırıldı")


# ============ CONTENT MODERATION ============

@router.get("/posts", response_model=PaginatedResponse)
async def get_all_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[PostStatus] = None,
    search: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all posts for moderation"""
    query = select(Post)
    
    if status_filter:
        query = query.where(Post.status == status_filter)
    
    if search:
        query = query.where(Post.content.ilike(f"%{search}%"))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Post.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.post("/posts/{post_id}/remove", response_model=SuccessResponse)
async def remove_post(
    post_id: UUID,
    reason: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a post (moderation)"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    post.status = PostStatus.REMOVED
    post.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.REMOVE_CONTENT,
        target_type="post",
        target_id=post_id,
        details={"reason": reason},
    )
    
    return SuccessResponse(message="Post kaldırıldı")


# ============ REPORTS ============

@router.get("/reports", response_model=PaginatedResponse)
async def get_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[ReportStatus] = None,
    type_filter: Optional[ReportType] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all reports"""
    query = select(Report)
    
    if status_filter:
        query = query.where(Report.status == status_filter)
    
    if type_filter:
        query = query.where(Report.type == type_filter)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Report.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return PaginatedResponse(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    data: ReportUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update report status"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapor bulunamadı"
        )
    
    report.status = data.status
    report.resolution_note = data.admin_notes
    report.reviewed_by_id = admin.id
    report.reviewed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(report)
    
    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.RESOLVE_REPORT,
        target_type="report",
        target_id=report_id,
        details=data.model_dump(),
    )
    
    return ReportResponse.model_validate(report)


# ============ WITHDRAWALS ============

@router.get("/withdrawals", response_model=PaginatedResponse)
async def get_withdrawals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[WithdrawalStatus] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all withdrawal requests"""
    query = select(Withdrawal)
    
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
        items=[WithdrawalAdminResponse.model_validate(w) for w in withdrawals],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.post("/withdrawals/{withdrawal_id}/approve", response_model=SuccessResponse)
async def approve_withdrawal(
    withdrawal_id: UUID,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve and process a withdrawal"""
    result = await db.execute(
        select(Withdrawal).where(Withdrawal.id == withdrawal_id)
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
            detail="Bu çekim isteği zaten işlenmiş"
        )
    
    # Process the actual payment
    try:
        if withdrawal.payment_method == PaymentMethod.MONERO:
            tx_hash, _fee = await monero_service.send_payment(
                address=withdrawal.payout_address,
                amount=float(withdrawal.crypto_amount),
            )
        elif withdrawal.payment_method == PaymentMethod.BTCPAY:
            payout = await btcpay_service.create_payout(
                destination=withdrawal.payout_address,
                amount=float(withdrawal.crypto_amount),
            )
            tx_hash = payout.get("id")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz ödeme yöntemi"
            )
        
        withdrawal.status = WithdrawalStatus.COMPLETED
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.reviewed_by_id = admin.id
        withdrawal.reviewed_at = datetime.utcnow()
        withdrawal.tx_hash = tx_hash
        
        # Update user's wallet
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == withdrawal.user_id)
        )
        wallet = result.scalar_one_or_none()
        
        if wallet:
            wallet.pending_balance -= withdrawal.amount
            wallet.total_withdrawn += withdrawal.amount
        
        await db.commit()
        
        await log_admin_action(
            db=db,
            admin_id=admin.id,
            action=AdminAction.APPROVE_WITHDRAWAL,
            target_type="withdrawal",
            target_id=withdrawal_id,
            details={"tx_hash": tx_hash},
        )
        
        return SuccessResponse(message=f"Çekim onaylandı. TX: {tx_hash}")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ödeme işlemi başarısız: {str(e)}"
        )


@router.post("/withdrawals/{withdrawal_id}/reject", response_model=SuccessResponse)
async def reject_withdrawal(
    withdrawal_id: UUID,
    reason: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a withdrawal"""
    result = await db.execute(
        select(Withdrawal).where(Withdrawal.id == withdrawal_id)
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
            detail="Bu çekim isteği zaten işlenmiş"
        )
    
    # Return funds to user
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == withdrawal.user_id)
    )
    wallet = result.scalar_one_or_none()
    
    if wallet:
        wallet.balance += withdrawal.amount
        wallet.pending_balance -= withdrawal.amount
    
    withdrawal.status = WithdrawalStatus.REJECTED
    withdrawal.processed_at = datetime.utcnow()
    withdrawal.reviewed_by_id = admin.id
    withdrawal.reviewed_at = datetime.utcnow()
    withdrawal.rejection_reason = reason
    
    await db.commit()
    
    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.REJECT_WITHDRAWAL,
        target_type="withdrawal",
        target_id=withdrawal_id,
        details={"reason": reason},
    )
    
    return SuccessResponse(message="Çekim reddedildi")


# ============ TEST / MANUEL BAKİYE ============

@router.post("/credit")
async def admin_credit_wallet(
    payload: dict,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Test/operasyon: bir kullanıcının cüzdanına TL bakiye ekler.
    payload: { "username": "...", "amount": 100.0, "note": "..." }
    Gerçek kripto göndermeden tüm para akışını denemek için kullanılır.
    """
    username = (payload.get("username") or "").lower().strip()
    try:
        amount = float(payload.get("amount") or 0)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Geçersiz tutar")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Tutar 0'dan büyük olmalı")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    await wallet_service.credit(
        db,
        user.id,
        amount,
        TransactionType.DEPOSIT,
        description=payload.get("note") or "Manuel bakiye (admin)",
    )

    await log_admin_action(
        db=db, admin_id=admin.id, action=AdminAction.UPDATE_SETTINGS,
        target_type="wallet", target_id=user.id,
        details={"amount": amount, "username": username},
    )

    wallet = await wallet_service.get_or_create_wallet(db, user.id)
    return {"username": username, "balance": float(wallet.balance), "credited": amount}


@router.put("/users/{user_id}/balance")
async def admin_set_balance(
    user_id: UUID,
    payload: dict,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Bir kullanıcının bakiyesini KESİN değere ayarlar (admin tam yetki)."""
    try:
        new_balance = round(float(payload.get("balance")), 2)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Geçersiz bakiye")
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Bakiye negatif olamaz")

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    wallet = await wallet_service.get_or_create_wallet(db, user.id)
    old = float(wallet.balance)
    wallet.balance = new_balance
    diff = round(new_balance - old, 2)
    db.add(Transaction(
        user_id=user.id, recipient_id=user.id,
        type=TransactionType.DEPOSIT if diff >= 0 else TransactionType.REFUND,
        status=TransactionStatus.COMPLETED,
        amount=abs(diff), fee=0, net_amount=abs(diff), currency="TRY",
        payment_method=PaymentMethod.WALLET,
        description=f"Admin bakiye ayarı: {old} → {new_balance}",
    ))
    await db.commit()

    await log_admin_action(
        db=db, admin_id=admin.id, action=AdminAction.UPDATE_SETTINGS,
        target_type="wallet", target_id=user.id,
        details={"old": old, "new": new_balance},
    )
    return {"id": str(user.id), "username": user.username, "balance": new_balance}


@router.post("/credit-all")
async def admin_credit_all(
    payload: dict,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    TÜM kullanıcılara toplu TL bakiye ekler (lansman/test için).
    payload: { "amount": 10000, "note": "...", "set": false }
    set=true ise bakiyeyi KESİN değere ayarlar; aksi halde ekler.
    """
    try:
        amount = round(float(payload.get("amount") or 0), 2)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Geçersiz tutar")
    as_set = bool(payload.get("set"))
    if amount < 0:
        raise HTTPException(status_code=400, detail="Tutar negatif olamaz")

    users = (await db.execute(select(User))).scalars().all()
    count = 0
    for u in users:
        wallet = await wallet_service.get_or_create_wallet(db, u.id)
        old = float(wallet.balance)
        if as_set:
            wallet.balance = amount
            diff = round(amount - old, 2)
        else:
            wallet.balance = round(old + amount, 2)
            diff = amount
        if diff != 0:
            db.add(Transaction(
                user_id=u.id, recipient_id=u.id,
                type=TransactionType.DEPOSIT if diff >= 0 else TransactionType.REFUND,
                status=TransactionStatus.COMPLETED,
                amount=abs(diff), fee=0, net_amount=abs(diff), currency="TRY",
                payment_method=PaymentMethod.WALLET,
                description=payload.get("note") or "Toplu bakiye (admin)",
            ))
        count += 1
    await db.commit()

    await log_admin_action(
        db=db, admin_id=admin.id, action=AdminAction.UPDATE_SETTINGS,
        target_type="wallet", target_id=admin.id,
        details={"amount": amount, "set": as_set, "users": count},
    )
    return {"updated_users": count, "amount": amount, "set": as_set}


@router.put("/users/{user_id}/role")
async def set_user_role(
    user_id: UUID,
    payload: dict,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcı rolünü değiştir (user, creator, moderator, admin)."""
    new_role = (payload.get("role") or "").lower().strip()
    valid = {r.value for r in UserRole}
    if new_role not in valid:
        raise HTTPException(status_code=400, detail=f"Geçersiz rol. Geçerli: {', '.join(valid)}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    user.role = UserRole(new_role)
    if new_role in ("moderator", "admin", "creator"):
        user.is_creator = user.is_creator or new_role == "creator"
    await db.commit()

    await log_admin_action(
        db=db, admin_id=admin.id, action=AdminAction.UPDATE_USER,
        target_type="user", target_id=user.id, details={"role": new_role},
    )
    return {"id": str(user.id), "username": user.username, "role": new_role}


# ============ SITE SETTINGS ============

@router.get("/settings")
async def get_site_settings(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Platform ayarlarını getir"""
    return await get_platform_settings(db)


@router.put("/settings")
async def update_site_settings(
    data: SiteSettingsUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Platform ayarlarını güncelle"""
    updates = data.model_dump(exclude_unset=True)
    result = await update_platform_settings(db, updates)

    await log_admin_action(
        db=db,
        admin_id=admin.id,
        action=AdminAction.UPDATE_SETTINGS,
        target_type="settings",
        details=updates,
    )

    return result


# ============ ANNOUNCEMENTS ============

@router.get("/announcements", response_model=List[AnnouncementResponse])
async def get_announcements(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all announcements"""
    result = await db.execute(
        select(Announcement).order_by(Announcement.created_at.desc())
    )
    return result.scalars().all()


@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    data: AnnouncementCreate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new announcement"""
    announcement = Announcement(
        title=data.title,
        content=data.content,
        content_html=data.content,
        is_active=data.is_active,
        starts_at=data.starts_at,
        expires_at=data.ends_at,
        created_by_id=admin.id,
    )
    
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    
    return AnnouncementResponse.model_validate(announcement)


@router.delete("/announcements/{announcement_id}", response_model=SuccessResponse)
async def delete_announcement(
    announcement_id: UUID,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an announcement"""
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duyuru bulunamadı"
        )
    
    await db.delete(announcement)
    await db.commit()
    
    return SuccessResponse(message="Duyuru silindi")


# ============ ADMIN LOGS ============

@router.get("/logs", response_model=PaginatedResponse)
async def get_admin_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action_filter: Optional[AdminAction] = None,
    admin_id_filter: Optional[UUID] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin activity logs"""
    query = select(AdminLog)
    
    if action_filter:
        query = query.where(AdminLog.action == action_filter)
    
    if admin_id_filter:
        query = query.where(AdminLog.admin_id == admin_id_filter)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(AdminLog.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return PaginatedResponse(
        items=logs,
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )
