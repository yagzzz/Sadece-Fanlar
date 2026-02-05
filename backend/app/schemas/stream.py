"""
Stream schemas
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.stream import StreamStatus, StreamType, StreamAccessType


class StreamCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    access: Optional[StreamAccessType] = StreamAccessType.SUBSCRIBERS
    price: Optional[Decimal] = None
    is_recorded: Optional[bool] = True


class StreamUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    access: Optional[StreamAccessType] = None


class StreamResponse(BaseModel):
    id: UUID
    creator_id: UUID
    title: str
    description: Optional[str] = None
    access: StreamAccessType
    status: StreamStatus
    viewers_count: int = 0
    total_viewers: int = 0
    tips_total: float = 0
    duration: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    has_access: bool = True
    stream_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class StreamKeyResponse(BaseModel):
    stream_key: str
    rtmp_url: str
    stream_url: str


class StreamMessageCreate(BaseModel):
    content: str = Field(..., max_length=500)


class StreamMessageResponse(BaseModel):
    id: UUID
    stream_id: UUID
    user_id: UUID
    content: str
    is_creator: bool
    created_at: datetime
    
    # User info
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class StreamTipCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    message: Optional[str] = Field(None, max_length=200)


class ScheduledStreamCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    scheduled_at: datetime
    access: Optional[StreamAccessType] = StreamAccessType.SUBSCRIBERS
    notify_subscribers: Optional[bool] = True


class ScheduledStreamResponse(BaseModel):
    id: UUID
    creator_id: UUID
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    access: StreamAccessType
    notify_subscribers: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True
