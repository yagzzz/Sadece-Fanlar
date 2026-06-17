"""
Notification schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    type: NotificationType
    title: str
    # Model alanı "message"; frontend hem message hem body okuyabilir.
    message: str
    body: Optional[str] = None
    image_url: Optional[str] = None
    link: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationSettingsUpdate(BaseModel):
    email_new_subscriber: Optional[bool] = None
    email_new_message: Optional[bool] = None
    email_new_tip: Optional[bool] = None
    email_new_comment: Optional[bool] = None
    email_subscription_expiring: Optional[bool] = None
    email_marketing: Optional[bool] = None
    push_new_subscriber: Optional[bool] = None
    push_new_message: Optional[bool] = None
    push_new_tip: Optional[bool] = None
    push_new_comment: Optional[bool] = None
    push_new_like: Optional[bool] = None
    push_mentions: Optional[bool] = None
    site_new_subscriber: Optional[bool] = None
    site_new_message: Optional[bool] = None
    site_new_tip: Optional[bool] = None
    site_new_comment: Optional[bool] = None
    site_new_like: Optional[bool] = None
    site_mentions: Optional[bool] = None
    site_new_follower: Optional[bool] = None


class NotificationSettingsResponse(BaseModel):
    email_new_subscriber: bool = True
    email_new_message: bool = True
    email_new_tip: bool = True
    email_new_comment: bool = True
    email_subscription_expiring: bool = True
    email_marketing: bool = False
    push_new_subscriber: bool = True
    push_new_message: bool = True
    push_new_tip: bool = True
    push_new_comment: bool = True
    push_new_like: bool = True
    push_mentions: bool = True
    site_new_subscriber: bool = True
    site_new_message: bool = True
    site_new_tip: bool = True
    site_new_comment: bool = True
    site_new_like: bool = True
    site_mentions: bool = True
    site_new_follower: bool = True
    
    class Config:
        from_attributes = True
