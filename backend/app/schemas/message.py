"""
Message schemas
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class MessageMediaResponse(BaseModel):
    """Message media response"""
    id: UUID
    type: str  # image, video, audio
    url: str
    thumbnail_url: Optional[str]
    blur_url: Optional[str]
    duration: Optional[int]
    is_locked: bool = False
    
    class Config:
        from_attributes = True


class MessageUserResponse(BaseModel):
    """User info in message"""
    id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    is_verified_creator: bool = False
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Create a message"""
    # /messages/send için alıcı; /conversations/{id}/messages için yol parametresi kullanılır
    recipient_id: Optional[UUID] = Field(None, description="Alıcı kullanıcı ID'si (/send için)")
    text: Optional[str] = Field(None, max_length=2000, description="Mesaj metni")
    media_ids: List[UUID] = Field(default=[], description="Medya ID'leri")
    
    is_ppv: bool = Field(default=False, description="Ücretli mesaj mı?")
    ppv_price: Optional[float] = Field(None, ge=1, le=200, description="PPV fiyatı")
    
    tip_amount: Optional[float] = Field(None, ge=1, le=500, description="Bahşiş miktarı")


class MessageResponse(BaseModel):
    """Message response"""
    id: UUID
    sender: MessageUserResponse
    
    text: Optional[str]
    media: List[MessageMediaResponse]
    
    is_ppv: bool
    ppv_price: Optional[float]
    is_unlocked: bool
    
    tip_amount: Optional[float]
    
    is_read: bool
    read_at: Optional[datetime]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    other_user: MessageUserResponse
    
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str]
    
    unread_count: int
    is_blocked: bool
    is_muted: bool
    
    # Is this a new message request (not from subscriber)
    is_request: bool = False
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """List of conversations"""
    conversations: List[ConversationResponse]
    total: int
    has_more: bool
    unread_total: int = 0


class MassMessageCreate(BaseModel):
    """Create a mass message to all subscribers"""
    text: str = Field(..., min_length=1, max_length=2000, description="Mesaj metni")
    media_ids: List[UUID] = Field(default=[], description="Medya ID'leri")
    
    is_ppv: bool = Field(default=False, description="Ücretli mesaj mı?")
    ppv_price: Optional[float] = Field(None, ge=1, le=200, description="PPV fiyatı")
    
    # Target filter
    only_active_subscribers: bool = Field(default=True, description="Sadece aktif abonelere")
    only_renewed: bool = Field(default=False, description="Sadece yenilemiş abonelere")


class MassMessageResponse(BaseModel):
    """Mass message response"""
    id: UUID
    
    text: str
    is_ppv: bool
    ppv_price: Optional[float]
    
    recipients_count: int
    sent_count: int
    read_count: int
    unlocked_count: int
    
    is_sending: bool
    completed_at: Optional[datetime]
    
    created_at: datetime
    
    class Config:
        from_attributes = True
