"""
Content related models - Attachments, Bookmarks, Lists
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.post import MediaType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post


class Attachment(Base):
    """Reusable media attachments"""
    __tablename__ = "attachments"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    blur_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))
    
    # Video/Audio specific
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # HLS (for videos)
    hls_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_attachments_user_id', user_id),
        Index('idx_attachments_type', type),
    )


class UserBookmark(Base):
    """Bookmarked/saved posts"""
    __tablename__ = "user_bookmarks"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    post: Mapped["Post"] = relationship("Post")
    
    __table_args__ = (
        Index('idx_user_bookmarks_user_id', user_id),
        Index('idx_user_bookmarks_user_post', user_id, post_id, unique=True),
    )


class ListType(str, Enum):
    FOLLOWING = "following"
    BLOCKED = "blocked"
    MUTED = "muted"
    FAVORITES = "favorites"
    CUSTOM = "custom"


class UserList(Base):
    """User-created lists for organizing followed creators"""
    __tablename__ = "user_lists"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ListType] = mapped_column(SQLEnum(ListType), default=ListType.CUSTOM)
    
    # Stats
    members_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    members: Mapped[List["UserListMember"]] = relationship("UserListMember", back_populates="list", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_lists_user_id', user_id),
        Index('idx_user_lists_type', type),
    )


class UserListMember(Base):
    """Members of user lists"""
    __tablename__ = "user_list_members"
    
    list_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_lists.id", ondelete="CASCADE"))
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    list: Mapped["UserList"] = relationship("UserList", back_populates="members")
    member: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_user_list_members_list_id', list_id),
        Index('idx_user_list_members_list_member', list_id, member_id, unique=True),
    )
