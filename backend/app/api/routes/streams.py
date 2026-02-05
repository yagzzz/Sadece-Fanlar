"""
Live Streaming API routes
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
import hashlib
import time

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.core.database import get_db
from app.core.config import settings
from app.core.redis import redis_client
from app.models.user import User
from app.models.stream import (
    LiveStream,
    StreamStatus,
    StreamAccessType,
    StreamViewer,
    StreamMessage,
    StreamTip,
    ScheduledStream,
)
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentMethod, Wallet
from app.schemas.stream import (
    StreamCreate,
    StreamUpdate,
    StreamResponse,
    StreamKeyResponse,
    StreamMessageCreate,
    StreamMessageResponse,
    StreamTipCreate,
    ScheduledStreamCreate,
    ScheduledStreamResponse,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.api.deps import get_current_user
from app.api.routes.notifications import create_notification
from app.models.notification import NotificationType

router = APIRouter(prefix="/streams", tags=["Live Streaming"])


def generate_stream_key(user_id: UUID) -> str:
    """Generate a unique stream key"""
    random_part = uuid4().hex[:12]
    timestamp = str(int(time.time()))
    hash_input = f"{user_id}{random_part}{timestamp}{settings.secret_key}"
    hash_part = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    return f"live_{random_part}_{hash_part}"


# ============ STREAM MANAGEMENT ============

@router.get("/my", response_model=List[StreamResponse])
async def get_my_streams(
    status_filter: Optional[StreamStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get creator's streams"""
    query = select(LiveStream).where(LiveStream.creator_id == current_user.id)
    
    if status_filter:
        query = query.where(LiveStream.status == status_filter)
    
    query = query.order_by(LiveStream.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    streams = result.scalars().all()
    
    return [StreamResponse.model_validate(s) for s in streams]


@router.post("/start", response_model=StreamResponse)
async def start_stream(
    data: StreamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new live stream"""
    # Check if already streaming
    result = await db.execute(
        select(LiveStream)
        .where(
            and_(
                LiveStream.creator_id == current_user.id,
                LiveStream.status == StreamStatus.LIVE
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten aktif bir yayınınız var"
        )
    
    # Generate stream key
    stream_key = generate_stream_key(current_user.id)
    
    stream = LiveStream(
        creator_id=current_user.id,
        title=data.title,
        description=data.description,
        access=data.access or StreamAccessType.SUBSCRIBERS,
        status=StreamStatus.PENDING,
        stream_key=stream_key,
        price=data.price if data.access == StreamAccessType.PAID else None,
        is_recorded=data.is_recorded or False,
    )
    
    db.add(stream)
    await db.commit()
    await db.refresh(stream)
    
    # Notify subscribers about new stream
    result = await db.execute(
        select(Subscription.subscriber_id)
        .where(
            and_(
                Subscription.creator_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    subscriber_ids = [s[0] for s in result.all()]
    
    for subscriber_id in subscriber_ids:
        await create_notification(
            db=db,
            user_id=subscriber_id,
            type=NotificationType.NEW_STREAM,
            title="Yeni Canlı Yayın",
            body=f"{current_user.display_name or current_user.username} canlı yayına başladı: {data.title}",
            actor_id=current_user.id,
            reference_type="stream",
            reference_id=stream.id,
            image_url=current_user.avatar_url,
        )
    
    return StreamResponse.model_validate(stream)


@router.get("/key", response_model=StreamKeyResponse)
async def get_stream_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get or regenerate stream key"""
    # Get current pending/live stream
    result = await db.execute(
        select(LiveStream)
        .where(
            and_(
                LiveStream.creator_id == current_user.id,
                LiveStream.status.in_([StreamStatus.PENDING, StreamStatus.LIVE])
            )
        )
        .order_by(LiveStream.created_at.desc())
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif yayın bulunamadı. Önce yayın başlatın."
        )
    
    return StreamKeyResponse(
        stream_key=stream.stream_key,
        rtmp_url=f"rtmp://{settings.stream_server_host}/live",
        stream_url=f"https://{settings.stream_server_host}/hls/{stream.stream_key}/index.m3u8",
    )


@router.post("/key/regenerate", response_model=StreamKeyResponse)
async def regenerate_stream_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Regenerate stream key"""
    result = await db.execute(
        select(LiveStream)
        .where(
            and_(
                LiveStream.creator_id == current_user.id,
                LiveStream.status == StreamStatus.PENDING
            )
        )
        .order_by(LiveStream.created_at.desc())
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif yayın bulunamadı"
        )
    
    if stream.status == StreamStatus.LIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Canlı yayın sırasında anahtar yenilenemez"
        )
    
    stream.stream_key = generate_stream_key(current_user.id)
    await db.commit()
    
    return StreamKeyResponse(
        stream_key=stream.stream_key,
        rtmp_url=f"rtmp://{settings.stream_server_host}/live",
        stream_url=f"https://{settings.stream_server_host}/hls/{stream.stream_key}/index.m3u8",
    )


@router.post("/{stream_id}/end", response_model=SuccessResponse)
async def end_stream(
    stream_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """End a live stream"""
    result = await db.execute(
        select(LiveStream)
        .where(
            and_(
                LiveStream.id == stream_id,
                LiveStream.creator_id == current_user.id
            )
        )
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yayın bulunamadı"
        )
    
    if stream.status == StreamStatus.ENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yayın zaten sonlandırılmış"
        )
    
    stream.status = StreamStatus.ENDED
    stream.ended_at = datetime.utcnow()
    
    if stream.started_at:
        stream.duration = int((stream.ended_at - stream.started_at).total_seconds())
    
    await db.commit()
    
    return SuccessResponse(message="Yayın sonlandırıldı")


@router.put("/{stream_id}", response_model=StreamResponse)
async def update_stream(
    stream_id: UUID,
    data: StreamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update stream details"""
    result = await db.execute(
        select(LiveStream)
        .where(
            and_(
                LiveStream.id == stream_id,
                LiveStream.creator_id == current_user.id
            )
        )
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yayın bulunamadı"
        )
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(stream, field, value)
    
    await db.commit()
    await db.refresh(stream)
    
    return StreamResponse.model_validate(stream)


# ============ WATCHING STREAMS ============

@router.get("/live", response_model=List[StreamResponse])
async def get_live_streams(
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all currently live streams"""
    query = (
        select(LiveStream)
        .where(LiveStream.status == StreamStatus.LIVE)
        .order_by(LiveStream.viewers_count.desc())
    )
    
    result = await db.execute(query)
    streams = result.scalars().all()
    
    # Filter based on access
    accessible_streams = []
    for stream in streams:
        if stream.access == StreamAccessType.FREE:
            accessible_streams.append(stream)
        elif current_user:
            if stream.access == StreamAccessType.SUBSCRIBERS:
                # Check subscription
                result = await db.execute(
                    select(Subscription)
                    .where(
                        and_(
                            Subscription.subscriber_id == current_user.id,
                            Subscription.creator_id == stream.creator_id,
                            Subscription.status == SubscriptionStatus.ACTIVE
                        )
                    )
                )
                if result.scalar_one_or_none():
                    accessible_streams.append(stream)
            elif stream.access == StreamAccessType.PAID:
                # Check if purchased
                result = await db.execute(
                    select(Transaction)
                    .where(
                        and_(
                            Transaction.user_id == current_user.id,
                            Transaction.stream_id == stream.id,
                            Transaction.status == TransactionStatus.COMPLETED
                        )
                    )
                )
                if result.scalar_one_or_none():
                    accessible_streams.append(stream)
    
    return [StreamResponse.model_validate(s) for s in accessible_streams]


@router.get("/{stream_id}", response_model=StreamResponse)
async def get_stream(
    stream_id: UUID,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get stream details"""
    result = await db.execute(
        select(LiveStream).where(LiveStream.id == stream_id)
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yayın bulunamadı"
        )
    
    # Check access
    has_access = False
    
    if stream.access == StreamAccessType.FREE:
        has_access = True
    elif current_user:
        if stream.creator_id == current_user.id:
            has_access = True
        elif stream.access == StreamAccessType.SUBSCRIBERS:
            result = await db.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.subscriber_id == current_user.id,
                        Subscription.creator_id == stream.creator_id,
                        Subscription.status == SubscriptionStatus.ACTIVE
                    )
                )
            )
            if result.scalar_one_or_none():
                has_access = True
        elif stream.access == StreamAccessType.PAID:
            result = await db.execute(
                select(Transaction)
                .where(
                    and_(
                        Transaction.user_id == current_user.id,
                        Transaction.stream_id == stream.id,
                        Transaction.status == TransactionStatus.COMPLETED
                    )
                )
            )
            if result.scalar_one_or_none():
                has_access = True
    
    response = StreamResponse.model_validate(stream)
    response.has_access = has_access
    
    if not has_access:
        response.stream_url = None  # Don't expose stream URL
    
    return response


@router.post("/{stream_id}/join", response_model=dict)
async def join_stream(
    stream_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a stream as viewer"""
    result = await db.execute(
        select(LiveStream).where(LiveStream.id == stream_id)
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yayın bulunamadı"
        )
    
    if stream.status != StreamStatus.LIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yayın şu an canlı değil"
        )
    
    # Check access for subscriber/PPV streams
    if stream.access == StreamAccessType.SUBSCRIBERS:
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.subscriber_id == current_user.id,
                    Subscription.creator_id == stream.creator_id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu yayını izlemek için abone olmalısınız"
            )
    
    elif stream.access == StreamAccessType.PAID:
        result = await db.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.user_id == current_user.id,
                    Transaction.stream_id == stream.id,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu yayını izlemek için ${stream.price} ödemeniz gerekiyor"
            )
    
    # Add viewer record
    result = await db.execute(
        select(StreamViewer)
        .where(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.user_id == current_user.id
            )
        )
    )
    viewer = result.scalar_one_or_none()
    
    if not viewer:
        viewer = StreamViewer(
            stream_id=stream_id,
            user_id=current_user.id,
        )
        db.add(viewer)
        stream.viewers_count = (stream.viewers_count or 0) + 1
        stream.total_viewers = (stream.total_viewers or 0) + 1
    else:
        viewer.left_at = None  # Rejoining
        stream.viewers_count = (stream.viewers_count or 0) + 1
    
    await db.commit()
    
    return {
        "stream_url": f"https://{settings.stream_server_host}/hls/{stream.stream_key}/index.m3u8",
        "viewer_count": stream.viewers_count,
    }


@router.post("/{stream_id}/leave", response_model=SuccessResponse)
async def leave_stream(
    stream_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a stream"""
    result = await db.execute(
        select(StreamViewer)
        .where(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.user_id == current_user.id
            )
        )
    )
    viewer = result.scalar_one_or_none()
    
    if viewer:
        viewer.left_at = datetime.utcnow()
        
        # Update viewer count
        result = await db.execute(
            select(LiveStream).where(LiveStream.id == stream_id)
        )
        stream = result.scalar_one_or_none()
        
        if stream and stream.viewer_count:
            stream.viewer_count = max(0, stream.viewer_count - 1)
        
        await db.commit()
    
    return SuccessResponse(message="Yayından ayrıldınız")


# ============ STREAM CHAT ============

@router.get("/{stream_id}/messages", response_model=List[StreamMessageResponse])
async def get_stream_messages(
    stream_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    before: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get stream chat messages"""
    query = select(StreamMessage).where(StreamMessage.stream_id == stream_id)
    
    if before:
        query = query.where(StreamMessage.created_at < before)
    
    query = query.order_by(StreamMessage.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    messages = list(reversed(result.scalars().all()))
    
    return [StreamMessageResponse.model_validate(m) for m in messages]


@router.post("/{stream_id}/messages", response_model=StreamMessageResponse)
async def send_stream_message(
    stream_id: UUID,
    data: StreamMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message in stream"""
    result = await db.execute(
        select(LiveStream).where(LiveStream.id == stream_id)
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yayın bulunamadı"
        )
    
    if stream.status != StreamStatus.LIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yayın şu an canlı değil"
        )
    
    message = StreamMessage(
        stream_id=stream_id,
        user_id=current_user.id,
        content=data.content,
        is_creator=stream.creator_id == current_user.id,
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return StreamMessageResponse.model_validate(message)


# ============ STREAM TIPS ============

@router.post("/{stream_id}/tip", response_model=dict)
async def send_stream_tip(
    stream_id: UUID,
    data: StreamTipCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a tip during stream"""
    result = await db.execute(
        select(LiveStream).where(LiveStream.id == stream_id)
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yayın bulunamadı"
        )
    
    # Check wallet balance
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet or wallet.balance < data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yetersiz bakiye"
        )
    
    # Process tip
    platform_fee = data.amount * (settings.platform_fee_percent / 100)
    net_amount = data.amount - platform_fee
    
    wallet.balance -= data.amount
    wallet.total_spent += data.amount
    
    # Credit creator
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == stream.creator_id)
    )
    creator_wallet = result.scalar_one_or_none()
    
    if creator_wallet:
        creator_wallet.balance += net_amount
        creator_wallet.total_earned += net_amount
    
    # Create tip record
    tip = StreamTip(
        stream_id=stream_id,
        user_id=current_user.id,
        amount=data.amount,
        message=data.message,
    )
    db.add(tip)
    
    # Update stream totals
    stream.tips_total = (stream.tips_total or 0) + data.amount
    
    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        recipient_id=stream.creator_id,
        type=TransactionType.STREAM_TIP,
        status=TransactionStatus.COMPLETED,
        amount=data.amount,
        fee=platform_fee,
        net_amount=net_amount,
        payment_method=PaymentMethod.WALLET,
        reference_type="stream",
        reference_id=stream_id,
    )
    db.add(transaction)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Bahşiş gönderildi",
        "tip_id": str(tip.id),
    }


# ============ SCHEDULED STREAMS ============

@router.get("/scheduled", response_model=List[ScheduledStreamResponse])
async def get_scheduled_streams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get creator's scheduled streams"""
    result = await db.execute(
        select(ScheduledStream)
        .where(
            and_(
                ScheduledStream.creator_id == current_user.id,
                ScheduledStream.scheduled_at > datetime.utcnow()
            )
        )
        .order_by(ScheduledStream.scheduled_at)
    )
    scheduled = result.scalars().all()
    
    return [ScheduledStreamResponse.model_validate(s) for s in scheduled]


@router.post("/schedule", response_model=ScheduledStreamResponse)
async def schedule_stream(
    data: ScheduledStreamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a future stream"""
    if data.scheduled_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Planlanan tarih gelecekte olmalı"
        )
    
    scheduled = ScheduledStream(
        creator_id=current_user.id,
        title=data.title,
        description=data.description,
        scheduled_at=data.scheduled_at,
        access=data.access or StreamAccessType.SUBSCRIBERS,
        notify_subscribers=data.notify_subscribers or True,
    )
    
    db.add(scheduled)
    await db.commit()
    await db.refresh(scheduled)
    
    return ScheduledStreamResponse.model_validate(scheduled)


# ============ RTMP AUTHENTICATION CALLBACK ============

@router.post("/auth/publish")
async def rtmp_publish_auth(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """RTMP server callback for stream authentication"""
    form = await request.form()
    stream_key = form.get("name") or form.get("key")
    
    if not stream_key:
        raise HTTPException(status_code=403, detail="No stream key")
    
    # Find stream by key
    result = await db.execute(
        select(LiveStream)
        .where(
            and_(
                LiveStream.stream_key == stream_key,
                LiveStream.status.in_([StreamStatus.PENDING, StreamStatus.LIVE])
            )
        )
    )
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=403, detail="Invalid stream key")
    
    # Update stream status
    if stream.status == StreamStatus.PENDING:
        stream.status = StreamStatus.LIVE
        stream.started_at = datetime.utcnow()
        await db.commit()
    
    return {"status": "ok"}


@router.post("/auth/done")
async def rtmp_done_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """RTMP server callback when stream ends"""
    form = await request.form()
    stream_key = form.get("name") or form.get("key")
    
    if stream_key:
        result = await db.execute(
            select(LiveStream).where(LiveStream.stream_key == stream_key)
        )
        stream = result.scalar_one_or_none()
        
        if stream and stream.status == StreamStatus.LIVE:
            stream.status = StreamStatus.ENDED
            stream.ended_at = datetime.utcnow()
            
            if stream.started_at:
                stream.duration = int((stream.ended_at - stream.started_at).total_seconds())
            
            await db.commit()
    
    return {"status": "ok"}
