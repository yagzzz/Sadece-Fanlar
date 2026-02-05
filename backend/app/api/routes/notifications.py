"""
Notification API routes
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func

from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationSettings
from app.schemas.notification import (
    NotificationResponse,
    NotificationSettingsUpdate,
    NotificationSettingsResponse,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.api.deps import get_current_user, get_current_user_ws

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# WebSocket connection manager for notifications
class NotificationConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_notification(self, notification: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(notification)
            except:
                self.disconnect(user_id)


notification_manager = NotificationConnectionManager()


@router.websocket("/ws/{token}")
async def websocket_notifications(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications"""
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=4001)
        return
    
    await notification_manager.connect(websocket, str(user.id))
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_json()
            
            # Handle mark as read
            if data.get("type") == "mark_read":
                notification_id = data.get("notification_id")
                if notification_id:
                    await db.execute(
                        update(Notification)
                        .where(
                            and_(
                                Notification.id == UUID(notification_id),
                                Notification.user_id == user.id
                            )
                        )
                        .values(read_at=datetime.utcnow())
                    )
                    await db.commit()
    
    except WebSocketDisconnect:
        notification_manager.disconnect(str(user.id))


@router.get("/", response_model=PaginatedResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    type_filter: Optional[NotificationType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notifications"""
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    
    if type_filter:
        query = query.where(Notification.type == type_filter)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get results
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return PaginatedResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        has_next=page * limit < total,
        has_prev=page > 1,
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get unread notification count"""
    result = await db.execute(
        select(func.count(Notification.id))
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.read_at.is_(None)
            )
        )
    )
    count = result.scalar() or 0
    
    return {"unread_count": count}


@router.post("/mark-read/{notification_id}", response_model=SuccessResponse)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read"""
    result = await db.execute(
        select(Notification)
        .where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bildirim bulunamadı"
        )
    
    notification.read_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Bildirim okundu olarak işaretlendi")


@router.post("/mark-all-read", response_model=SuccessResponse)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    await db.execute(
        update(Notification)
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.read_at.is_(None)
            )
        )
        .values(read_at=datetime.utcnow())
    )
    await db.commit()
    
    return SuccessResponse(message="Tüm bildirimler okundu olarak işaretlendi")


@router.delete("/{notification_id}", response_model=SuccessResponse)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    result = await db.execute(
        select(Notification)
        .where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bildirim bulunamadı"
        )
    
    await db.delete(notification)
    await db.commit()
    
    return SuccessResponse(message="Bildirim silindi")


@router.delete("/", response_model=SuccessResponse)
async def clear_all_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all notifications"""
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        await db.delete(notification)
    
    await db.commit()
    
    return SuccessResponse(message="Tüm bildirimler silindi")


# ============ NOTIFICATION SETTINGS ============

@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get notification settings"""
    result = await db.execute(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return NotificationSettingsResponse(
        email_new_subscriber=settings.email_new_subscriber,
        email_new_message=settings.email_new_message,
        email_new_tip=settings.email_new_tip,
        email_new_comment=settings.email_new_comment,
        email_subscription_expiring=settings.email_subscription_expiring,
        email_marketing=settings.email_marketing,
        push_new_subscriber=settings.push_new_subscriber,
        push_new_message=settings.push_new_message,
        push_new_tip=settings.push_new_tip,
        push_new_comment=settings.push_new_comment,
        push_new_like=settings.push_new_like,
        push_mentions=settings.push_mentions,
        site_new_subscriber=settings.site_new_subscriber,
        site_new_message=settings.site_new_message,
        site_new_tip=settings.site_new_tip,
        site_new_comment=settings.site_new_comment,
        site_new_like=settings.site_new_like,
        site_mentions=settings.site_mentions,
        site_new_follower=settings.site_new_follower,
    )


@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    data: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update notification settings"""
    result = await db.execute(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.add(settings)
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return NotificationSettingsResponse.model_validate(settings)


# ============ HELPER FUNCTION TO CREATE NOTIFICATIONS ============

async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    type: NotificationType,
    title: str,
    body: str,
    data: Optional[dict] = None,
    actor_id: Optional[UUID] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[UUID] = None,
    image_url: Optional[str] = None,
):
    """Create and send a notification"""
    # Check user's notification settings
    result = await db.execute(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()
    
    # Check if this notification type is enabled
    setting_map = {
        NotificationType.NEW_SUBSCRIBER: "site_new_subscriber",
        NotificationType.NEW_MESSAGE: "site_new_message",
        NotificationType.NEW_TIP: "site_new_tip",
        NotificationType.NEW_COMMENT: "site_new_comment",
        NotificationType.NEW_LIKE: "site_new_like",
        NotificationType.MENTION: "site_mentions",
        NotificationType.NEW_FOLLOWER: "site_new_follower",
    }
    
    setting_name = setting_map.get(type)
    if settings and setting_name:
        if not getattr(settings, setting_name, True):
            return None  # User has disabled this notification type
    
    # Create notification
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        data=data,
        actor_id=actor_id,
        reference_type=reference_type,
        reference_id=reference_id,
        image_url=image_url,
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    # Send via WebSocket
    await notification_manager.send_notification(
        {
            "type": "notification",
            "notification": NotificationResponse.model_validate(notification).model_dump(),
        },
        str(user_id)
    )
    
    # TODO: Send push notification
    # TODO: Send email notification (based on settings)
    
    return notification
