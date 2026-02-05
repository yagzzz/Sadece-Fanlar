"""
Messaging API routes with WebSocket support
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.redis import redis_client
from app.models.user import User
from app.models.message import Message, Conversation, ConversationParticipant, MassMessage, MessageMedia
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentMethod, Wallet
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ConversationListResponse,
    MassMessageCreate,
    MassMessageResponse,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.api.deps import get_current_user, get_current_user_ws

router = APIRouter(prefix="/messages", tags=["Messages"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast_to_users(self, message: dict, user_ids: list[str]):
        for user_id in user_ids:
            if user_id in self.active_connections:
                await self.active_connections[user_id].send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time messaging"""
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=4001)
        return
    
    await manager.connect(websocket, str(user.id))
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "typing":
                # Broadcast typing indicator
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    # Get other participants
                    result = await db.execute(
                        select(ConversationParticipant.user_id)
                        .where(
                            and_(
                                ConversationParticipant.conversation_id == UUID(conversation_id),
                                ConversationParticipant.user_id != user.id
                            )
                        )
                    )
                    participants = [str(p[0]) for p in result.all()]
                    
                    await manager.broadcast_to_users(
                        {
                            "type": "typing",
                            "conversation_id": conversation_id,
                            "user_id": str(user.id),
                            "username": user.username,
                        },
                        participants
                    )
            
            elif data.get("type") == "read":
                # Mark messages as read
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    await db.execute(
                        update(Message)
                        .where(
                            and_(
                                Message.conversation_id == UUID(conversation_id),
                                Message.sender_id != user.id,
                                Message.read_at.is_(None)
                            )
                        )
                        .values(read_at=datetime.utcnow())
                    )
                    await db.commit()
    
    except WebSocketDisconnect:
        manager.disconnect(str(user.id))


# ============ CONVERSATIONS ============

@router.get("/conversations", response_model=PaginatedResponse)
async def get_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversations"""
    # Get conversation IDs where user is participant
    subquery = (
        select(ConversationParticipant.conversation_id)
        .where(ConversationParticipant.user_id == current_user.id)
    )
    
    # Get conversations with last message
    query = (
        select(Conversation)
        .where(Conversation.id.in_(subquery))
        .options(selectinload(Conversation.participants))
        .order_by(Conversation.last_message_at.desc().nullslast())
    )
    
    # Count
    count_query = select(func.count()).select_from(
        select(Conversation.id).where(Conversation.id.in_(subquery)).subquery()
    )
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    # Build response with unread counts
    items = []
    for conv in conversations:
        # Get unread count
        unread_result = await db.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.conversation_id == conv.id,
                    Message.sender_id != current_user.id,
                    Message.read_at.is_(None)
                )
            )
        )
        unread_count = unread_result.scalar() or 0
        
        # Get other participant
        other_user = None
        for p in conv.participants:
            if p.user_id != current_user.id:
                user_result = await db.execute(
                    select(User).where(User.id == p.user_id)
                )
                other_user = user_result.scalar_one_or_none()
                break
        
        items.append(ConversationListResponse(
            id=conv.id,
            other_user={
                "id": other_user.id if other_user else None,
                "username": other_user.username if other_user else "Unknown",
                "display_name": other_user.display_name if other_user else "Unknown",
                "avatar_url": other_user.avatar_url if other_user else None,
            } if other_user else None,
            last_message=conv.last_message_text,
            last_message_at=conv.last_message_at,
            unread_count=unread_count,
            is_muted=False,  # TODO: Implement muting
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation details"""
    # Check if user is participant
    result = await db.execute(
        select(ConversationParticipant)
        .where(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == current_user.id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konuşma bulunamadı"
        )
    
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.participants))
    )
    conversation = result.scalar_one_or_none()
    
    return ConversationResponse(
        id=conversation.id,
        created_at=conversation.created_at,
        last_message_at=conversation.last_message_at,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=PaginatedResponse)
async def get_conversation_messages(
    conversation_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    before: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages in a conversation"""
    # Check if user is participant
    result = await db.execute(
        select(ConversationParticipant)
        .where(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == current_user.id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konuşma bulunamadı"
        )
    
    query = select(Message).where(Message.conversation_id == conversation_id)
    
    if before:
        query = query.where(Message.created_at < before)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get messages (newest first for pagination, reverse later)
    query = query.order_by(Message.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    messages = list(reversed(result.scalars().all()))
    
    # Mark as read
    await db.execute(
        update(Message)
        .where(
            and_(
                Message.conversation_id == conversation_id,
                Message.sender_id != current_user.id,
                Message.read_at.is_(None)
            )
        )
        .values(read_at=datetime.utcnow())
    )
    await db.commit()
    
    return PaginatedResponse(
        items=[MessageResponse.model_validate(m) for m in messages],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.post("/send", response_model=MessageResponse)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to another user"""
    # Get recipient
    result = await db.execute(select(User).where(User.id == data.recipient_id))
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinize mesaj gönderemezsiniz"
        )
    
    # Check messaging restrictions
    if recipient.messages_restriction == "subscribers":
        # Check if sender is subscribed to recipient
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.subscriber_id == current_user.id,
                    Subscription.creator_id == recipient.id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu kullanıcıya mesaj gönderebilmek için abone olmalısınız"
            )
    
    elif recipient.messages_restriction == "paid":
        # Check message price
        if recipient.message_price and recipient.message_price > 0:
            # Check wallet
            result = await db.execute(
                select(Wallet).where(Wallet.user_id == current_user.id)
            )
            wallet = result.scalar_one_or_none()
            
            if not wallet or wallet.balance < float(recipient.message_price):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mesaj göndermek için ${recipient.message_price} gerekiyor. Yetersiz bakiye."
                )
            
            # Deduct message price
            platform_fee = float(recipient.message_price) * (settings.platform_fee_percent / 100)
            net_amount = float(recipient.message_price) - platform_fee
            
            wallet.balance -= float(recipient.message_price)
            wallet.total_spent += float(recipient.message_price)
            
            # Credit recipient
            result = await db.execute(
                select(Wallet).where(Wallet.user_id == recipient.id)
            )
            recipient_wallet = result.scalar_one_or_none()
            if recipient_wallet:
                recipient_wallet.balance += net_amount
                recipient_wallet.total_earned += net_amount
            
            # Create transaction
            transaction = Transaction(
                user_id=current_user.id,
                recipient_id=recipient.id,
                type=TransactionType.MESSAGE,
                status=TransactionStatus.COMPLETED,
                amount=float(recipient.message_price),
                fee=platform_fee,
                net_amount=net_amount,
                payment_method=PaymentMethod.WALLET,
            )
            db.add(transaction)
    
    # Find or create conversation
    # Look for existing conversation between these two users
    result = await db.execute(
        select(Conversation)
        .join(ConversationParticipant)
        .where(
            and_(
                ConversationParticipant.user_id == current_user.id,
                Conversation.id.in_(
                    select(ConversationParticipant.conversation_id)
                    .where(ConversationParticipant.user_id == recipient.id)
                )
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        # Create new conversation
        conversation = Conversation()
        db.add(conversation)
        await db.flush()
        
        # Add participants
        db.add(ConversationParticipant(
            conversation_id=conversation.id,
            user_id=current_user.id
        ))
        db.add(ConversationParticipant(
            conversation_id=conversation.id,
            user_id=recipient.id
        ))
    
    # Create message
    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        content=data.content,
        is_ppv=data.is_ppv or False,
        ppv_price=data.ppv_price if data.is_ppv else None,
    )
    db.add(message)
    
    # Update conversation
    conversation.last_message_at = datetime.utcnow()
    conversation.last_message_text = data.content[:100] if data.content else "[Medya]"
    
    await db.commit()
    await db.refresh(message)
    
    # Send via WebSocket if recipient is connected
    await manager.send_personal_message(
        {
            "type": "new_message",
            "message": MessageResponse.model_validate(message).model_dump(),
        },
        str(recipient.id)
    )
    
    return MessageResponse.model_validate(message)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message_to_conversation(
    conversation_id: UUID,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to an existing conversation"""
    # Check if user is participant
    result = await db.execute(
        select(ConversationParticipant)
        .where(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == current_user.id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konuşma bulunamadı"
        )
    
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=data.content,
        is_ppv=data.is_ppv or False,
        ppv_price=data.ppv_price if data.is_ppv else None,
    )
    db.add(message)
    
    # Update conversation
    conversation.last_message_at = datetime.utcnow()
    conversation.last_message_text = data.content[:100] if data.content else "[Medya]"
    
    await db.commit()
    await db.refresh(message)
    
    # Notify other participants
    result = await db.execute(
        select(ConversationParticipant.user_id)
        .where(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id != current_user.id
            )
        )
    )
    other_participants = [str(p[0]) for p in result.all()]
    
    await manager.broadcast_to_users(
        {
            "type": "new_message",
            "message": MessageResponse.model_validate(message).model_dump(),
        },
        other_participants
    )
    
    return MessageResponse.model_validate(message)


# ============ MASS MESSAGES ============

@router.post("/mass", response_model=MassMessageResponse)
async def send_mass_message(
    data: MassMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to all subscribers (creators only)"""
    # Get subscriber count
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(
            and_(
                Subscription.creator_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    subscriber_count = result.scalar() or 0
    
    if subscriber_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hiç aktif aboneniz yok"
        )
    
    # Create mass message record
    mass_message = MassMessage(
        sender_id=current_user.id,
        content=data.content,
        is_ppv=data.is_ppv or False,
        ppv_price=data.ppv_price if data.is_ppv else None,
        total_recipients=subscriber_count,
        sent_count=0,
        status="pending",
    )
    db.add(mass_message)
    await db.commit()
    await db.refresh(mass_message)
    
    # TODO: Queue the actual sending as a background task
    # For now, we'll send immediately (not ideal for large subscriber counts)
    
    # Get all active subscribers
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
    
    # Send to each subscriber
    for subscriber_id in subscriber_ids:
        # Find or create conversation
        result = await db.execute(
            select(Conversation)
            .join(ConversationParticipant)
            .where(
                and_(
                    ConversationParticipant.user_id == current_user.id,
                    Conversation.id.in_(
                        select(ConversationParticipant.conversation_id)
                        .where(ConversationParticipant.user_id == subscriber_id)
                    )
                )
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            conversation = Conversation()
            db.add(conversation)
            await db.flush()
            
            db.add(ConversationParticipant(
                conversation_id=conversation.id,
                user_id=current_user.id
            ))
            db.add(ConversationParticipant(
                conversation_id=conversation.id,
                user_id=subscriber_id
            ))
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            sender_id=current_user.id,
            content=data.content,
            is_ppv=data.is_ppv or False,
            ppv_price=data.ppv_price if data.is_ppv else None,
            mass_message_id=mass_message.id,
        )
        db.add(message)
        
        # Update conversation
        conversation.last_message_at = datetime.utcnow()
        conversation.last_message_text = data.content[:100] if data.content else "[Medya]"
        
        mass_message.sent_count += 1
        
        # WebSocket notification
        await manager.send_personal_message(
            {
                "type": "new_message",
                "message": {
                    "content": data.content,
                    "sender_id": str(current_user.id),
                    "sender_username": current_user.username,
                    "is_ppv": data.is_ppv,
                }
            },
            str(subscriber_id)
        )
    
    mass_message.status = "completed"
    await db.commit()
    await db.refresh(mass_message)
    
    return MassMessageResponse(
        id=mass_message.id,
        content=mass_message.content,
        is_ppv=mass_message.is_ppv,
        ppv_price=float(mass_message.ppv_price) if mass_message.ppv_price else None,
        total_recipients=mass_message.total_recipients,
        sent_count=mass_message.sent_count,
        status=mass_message.status,
        created_at=mass_message.created_at,
    )


@router.delete("/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message (sender only)"""
    result = await db.execute(
        select(Message)
        .where(
            and_(
                Message.id == message_id,
                Message.sender_id == current_user.id
            )
        )
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesaj bulunamadı"
        )
    
    # Soft delete
    message.is_deleted = True
    message.content = "[Bu mesaj silindi]"
    
    await db.commit()
    
    return SuccessResponse(message="Mesaj silindi")
