"""
Posts API routes
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.post import Post, PostMedia, PostComment, PostReaction, PostStatus, MediaType
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.content import UserBookmark, Attachment
from app.services.storage import storage_service
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    PostMediaResponse,
    PostAuthorResponse,
    CommentCreate,
    CommentResponse,
    CommentListResponse,
    CommentAuthorResponse,
    ReactionCreate,
)
from app.schemas.common import SuccessResponse
from app.api.deps import get_current_user, get_current_user_optional, get_current_creator
import markdown
import bleach

router = APIRouter(prefix="/posts", tags=["Posts"])


def _build_post_author(user: User) -> PostAuthorResponse:
    return PostAuthorResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        is_verified_creator=user.is_verified_creator,
    )


def _build_comment_author(user: User) -> CommentAuthorResponse:
    return CommentAuthorResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )


def render_markdown(text: str) -> str:
    """Render markdown to HTML with sanitization"""
    if not text:
        return ""
    html = markdown.markdown(text, extensions=['nl2br', 'fenced_code'])
    return bleach.clean(
        html,
        tags=['p', 'br', 'strong', 'em', 'a', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote'],
        attributes={'a': ['href', 'title']},
    )


async def check_post_access(
    post: Post,
    user: Optional[User],
    db: AsyncSession
) -> tuple[bool, bool]:
    """
    Check if user can access post content
    Returns (can_view, is_unlocked)
    """
    # Author can always view their own posts
    if user and post.author_id == user.id:
        return True, True
    
    # Free profiles - everyone can view
    author = await db.get(User, post.author_id)
    if author and author.is_free_profile:
        if not post.is_ppv:
            return True, True
    
    # Check subscription
    if user:
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.subscriber_id == user.id,
                    Subscription.creator_id == post.author_id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Subscriber can view if post is free for subscribers
            if post.is_free_for_subscribers:
                return True, True
    
    # Check if user has unlocked PPV
    if user and post.is_ppv:
        result = await db.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user.id,
                    Transaction.post_id == post.id,
                    Transaction.type == TransactionType.POST_UNLOCK,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            )
        )
        if result.scalar_one_or_none():
            return True, True
    
    # Can see post exists but not content
    if post.is_ppv:
        return True, False
    
    # Non-subscribers can't view paid content
    if author and not author.is_free_profile:
        return True, False
    
    return True, True


@router.post("/media")
async def upload_post_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db),
):
    """
    Gönderi için medya yükle (resim/video/ses).
    Yüklenen dosya bir Attachment olarak saklanır; dönen `id` gönderi
    oluştururken `media_ids` içinde kullanılır.
    """
    content_type = (file.content_type or "").lower()

    try:
        if content_type in settings.allowed_image_types:
            info = await storage_service.upload_image(
                file, prefix="posts", create_thumbnail=True, create_blur=True
            )
            media_type = MediaType.IMAGE
        elif content_type in settings.allowed_video_types:
            info = await storage_service.upload_file(
                file, prefix="posts", allowed_types=settings.allowed_video_types
            )
            media_type = MediaType.VIDEO
        elif content_type in settings.allowed_audio_types:
            info = await storage_service.upload_file(
                file, prefix="posts", allowed_types=settings.allowed_audio_types
            )
            media_type = MediaType.AUDIO
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Desteklenmeyen dosya türü",
            )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Medya depolama servisine ulaşılamadı",
        )

    attachment = Attachment(
        user_id=current_user.id,
        type=media_type,
        url=info["url"],
        thumbnail_url=info.get("thumbnail_url"),
        blur_url=info.get("blur_url"),
        filename=info.get("filename", file.filename or "media"),
        original_filename=info.get("original_filename", file.filename or "media"),
        file_size=info.get("file_size", 0),
        mime_type=info.get("mime_type", content_type),
        width=info.get("width"),
        height=info.get("height"),
        is_processed=True,
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return {
        "id": str(attachment.id),
        "type": media_type.value,
        "url": attachment.url,
        "thumbnail_url": attachment.thumbnail_url,
    }


@router.get("/feed", response_model=PostListResponse)
async def get_feed(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=50),
    discover: bool = Query(default=False, description="True: tüm üreticilerden keşfet akışı"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Akış. Varsayılan: abone olunan üreticiler (+ kendi gönderileri).
    discover=True: TÜM üreticilerin herkese açık gönderileri (Keşfet sayfası);
    kilitli içerik bulanık önizleme olarak görünür (check_post_access).
    """
    offset = (page - 1) * per_page

    base_filters = [
        Post.status == PostStatus.APPROVED,
        Post.deleted_at.is_(None),
        or_(Post.release_date.is_(None), Post.release_date <= datetime.utcnow()),
        or_(Post.expire_date.is_(None), Post.expire_date > datetime.utcnow()),
    ]

    if discover:
        # Keşfet: tüm onaylı gönderiler; popülerlik + güncellik sıralaması
        query = (
            select(Post)
            .options(selectinload(Post.media), selectinload(Post.author))
            .where(and_(*base_filters))
            .order_by(desc(Post.likes_count), desc(Post.created_at))
            .offset(offset)
            .limit(per_page)
        )
        count_query = select(func.count(Post.id)).where(and_(*base_filters))
    else:
        # Get subscribed creator IDs
        result = await db.execute(
            select(Subscription.creator_id).where(
                and_(
                    Subscription.subscriber_id == current_user.id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        creator_ids = [row[0] for row in result.all()]
        # Include own posts
        creator_ids.append(current_user.id)

        query = (
            select(Post)
            .options(selectinload(Post.media), selectinload(Post.author))
            .where(and_(Post.author_id.in_(creator_ids), *base_filters))
            .order_by(desc(Post.is_pinned), desc(Post.created_at))
            .offset(offset)
            .limit(per_page)
        )
        count_query = select(func.count(Post.id)).where(
            and_(
                Post.author_id.in_(creator_ids),
                Post.status == PostStatus.APPROVED,
                Post.deleted_at.is_(None),
            )
        )

    result = await db.execute(query)
    posts = result.scalars().all()
    total = await db.scalar(count_query)
    
    # Build response with access checks
    post_responses = []
    for post in posts:
        can_view, is_unlocked = await check_post_access(post, current_user, db)
        
        # Check if liked
        result = await db.execute(
            select(PostReaction).where(
                and_(
                    PostReaction.post_id == post.id,
                    PostReaction.user_id == current_user.id
                )
            )
        )
        is_liked = result.scalar_one_or_none() is not None
        
        # Check if bookmarked
        result = await db.execute(
            select(UserBookmark).where(
                and_(
                    UserBookmark.post_id == post.id,
                    UserBookmark.user_id == current_user.id
                )
            )
        )
        is_bookmarked = result.scalar_one_or_none() is not None
        
        # Build media list
        media_list = []
        for m in post.media:
            media_list.append({
                "id": m.id,
                "type": m.type,
                "url": m.url if is_unlocked else m.blur_url,
                "thumbnail_url": m.thumbnail_url if is_unlocked else m.blur_url,
                "blur_url": m.blur_url,
                "duration": m.duration,
                "width": m.width,
                "height": m.height,
                "is_locked": not is_unlocked,
            })
        
        post_responses.append(PostResponse(
            id=post.id,
            author=_build_post_author(post.author),
            text=post.text if is_unlocked else None,
            text_html=post.text_html if is_unlocked else None,
            media=media_list,
            is_ppv=post.is_ppv,
            ppv_price=post.ppv_price,
            is_free_for_subscribers=post.is_free_for_subscribers,
            is_pinned=post.is_pinned,
            likes_count=post.likes_count,
            comments_count=post.comments_count,
            tips_total=float(post.tips_total),
            is_liked=is_liked,
            is_bookmarked=is_bookmarked,
            is_unlocked=is_unlocked,
            can_comment=post.author.allow_comments,
            created_at=post.created_at,
            release_date=post.release_date,
            expire_date=post.expire_date,
        ))
    
    return PostListResponse(
        posts=post_responses,
        total=total or 0,
        page=page,
        per_page=per_page,
        has_more=offset + len(posts) < (total or 0),
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post"""
    # Validate PPV
    if data.is_ppv and not data.ppv_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PPV içerik için fiyat belirtmelisiniz"
        )
    
    # Create post
    post = Post(
        author_id=current_user.id,
        text=data.text,
        text_html=render_markdown(data.text) if data.text else None,
        is_ppv=data.is_ppv,
        ppv_price=data.ppv_price,
        is_free_for_subscribers=data.is_free_for_subscribers,
        release_date=data.release_date,
        expire_date=data.expire_date,
        status=PostStatus.SCHEDULED if data.release_date else PostStatus.APPROVED,
    )
    db.add(post)
    await db.flush()
    
    # Attach media
    if data.media_ids:
        from app.models.content import Attachment
        for i, media_id in enumerate(data.media_ids):
            result = await db.execute(
                select(Attachment).where(
                    and_(
                        Attachment.id == media_id,
                        Attachment.user_id == current_user.id
                    )
                )
            )
            attachment = result.scalar_one_or_none()
            
            if attachment:
                post_media = PostMedia(
                    post_id=post.id,
                    type=attachment.type,
                    url=attachment.url,
                    thumbnail_url=attachment.thumbnail_url,
                    blur_url=attachment.blur_url,
                    filename=attachment.filename,
                    file_size=attachment.file_size,
                    mime_type=attachment.mime_type,
                    duration=attachment.duration,
                    width=attachment.width,
                    height=attachment.height,
                    is_processed=attachment.is_processed,
                    hls_url=attachment.hls_url,
                    sort_order=i,
                )
                db.add(post_media)
    
    # Update user post count
    current_user.posts_count += 1
    
    await db.commit()
    await db.refresh(post)
    
    # Return full response
    return PostResponse(
        id=post.id,
        author=_build_post_author(current_user),
        text=post.text,
        text_html=post.text_html,
        media=[],  # Will be populated on refresh
        is_ppv=post.is_ppv,
        ppv_price=post.ppv_price,
        is_free_for_subscribers=post.is_free_for_subscribers,
        is_pinned=post.is_pinned,
        likes_count=0,
        comments_count=0,
        tips_total=0,
        is_liked=False,
        is_bookmarked=False,
        is_unlocked=True,
        can_comment=True,
        created_at=post.created_at,
        release_date=post.release_date,
        expire_date=post.expire_date,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get a single post"""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.media), selectinload(Post.author))
        .where(
            and_(
                Post.id == post_id,
                Post.deleted_at.is_(None)
            )
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    can_view, is_unlocked = await check_post_access(post, current_user, db)
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu içeriği görüntüleme yetkiniz yok"
        )
    
    # Check reactions/bookmarks if logged in
    is_liked = False
    is_bookmarked = False
    
    if current_user:
        result = await db.execute(
            select(PostReaction).where(
                and_(
                    PostReaction.post_id == post.id,
                    PostReaction.user_id == current_user.id
                )
            )
        )
        is_liked = result.scalar_one_or_none() is not None
        
        result = await db.execute(
            select(UserBookmark).where(
                and_(
                    UserBookmark.post_id == post.id,
                    UserBookmark.user_id == current_user.id
                )
            )
        )
        is_bookmarked = result.scalar_one_or_none() is not None
    
    # Build media list
    media_list = []
    for m in post.media:
        media_list.append({
            "id": m.id,
            "type": m.type,
            "url": m.url if is_unlocked else m.blur_url,
            "thumbnail_url": m.thumbnail_url if is_unlocked else m.blur_url,
            "blur_url": m.blur_url,
            "duration": m.duration,
            "width": m.width,
            "height": m.height,
            "is_locked": not is_unlocked,
        })
    
    # Increment view count
    post.views_count += 1
    await db.commit()
    
    return PostResponse(
        id=post.id,
        author=_build_post_author(post.author),
        text=post.text if is_unlocked else None,
        text_html=post.text_html if is_unlocked else None,
        media=media_list,
        is_ppv=post.is_ppv,
        ppv_price=post.ppv_price,
        is_free_for_subscribers=post.is_free_for_subscribers,
        is_pinned=post.is_pinned,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        tips_total=float(post.tips_total),
        is_liked=is_liked,
        is_bookmarked=is_bookmarked,
        is_unlocked=is_unlocked,
        can_comment=post.author.allow_comments,
        created_at=post.created_at,
        release_date=post.release_date,
        expire_date=post.expire_date,
    )


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a post"""
    result = await db.execute(
        select(Post).where(
            and_(
                Post.id == post_id,
                Post.author_id == current_user.id,
                Post.deleted_at.is_(None)
            )
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    if "text" in update_data:
        update_data["text_html"] = render_markdown(update_data["text"])
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    await db.commit()
    
    return await get_post(post_id, current_user, db)


@router.delete("/{post_id}", response_model=SuccessResponse)
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a post (soft delete)"""
    result = await db.execute(
        select(Post).where(
            and_(
                Post.id == post_id,
                Post.author_id == current_user.id,
                Post.deleted_at.is_(None)
            )
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    post.deleted_at = datetime.utcnow()
    current_user.posts_count -= 1
    
    await db.commit()
    
    return SuccessResponse(message="Post silindi")


@router.post("/{post_id}/like", response_model=SuccessResponse)
async def like_post(
    post_id: UUID,
    data: ReactionCreate = ReactionCreate(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Like a post"""
    result = await db.execute(
        select(Post).where(
            and_(
                Post.id == post_id,
                Post.deleted_at.is_(None)
            )
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    # Check if already liked
    result = await db.execute(
        select(PostReaction).where(
            and_(
                PostReaction.post_id == post_id,
                PostReaction.user_id == current_user.id
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update reaction type
        existing.reaction_type = data.reaction_type
    else:
        # Create new reaction
        reaction = PostReaction(
            post_id=post_id,
            user_id=current_user.id,
            reaction_type=data.reaction_type,
        )
        db.add(reaction)
        post.likes_count += 1
        
        # Update author's likes count
        author = await db.get(User, post.author_id)
        if author:
            author.likes_count += 1
    
    await db.commit()
    
    return SuccessResponse(message="Beğenildi")


@router.delete("/{post_id}/like", response_model=SuccessResponse)
async def unlike_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlike a post"""
    result = await db.execute(
        select(PostReaction).where(
            and_(
                PostReaction.post_id == post_id,
                PostReaction.user_id == current_user.id
            )
        )
    )
    reaction = result.scalar_one_or_none()
    
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu postu beğenmemişsiniz"
        )
    
    await db.delete(reaction)
    
    # Update counts
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post:
        post.likes_count -= 1
        author = await db.get(User, post.author_id)
        if author:
            author.likes_count -= 1
    
    await db.commit()
    
    return SuccessResponse(message="Beğeni kaldırıldı")


@router.post("/{post_id}/bookmark", response_model=SuccessResponse)
async def bookmark_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bookmark a post"""
    # Check if already bookmarked
    result = await db.execute(
        select(UserBookmark).where(
            and_(
                UserBookmark.post_id == post_id,
                UserBookmark.user_id == current_user.id
            )
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu post zaten kaydedilmiş"
        )
    
    bookmark = UserBookmark(
        user_id=current_user.id,
        post_id=post_id,
    )
    db.add(bookmark)
    await db.commit()
    
    return SuccessResponse(message="Kaydedildi")


@router.delete("/{post_id}/bookmark", response_model=SuccessResponse)
async def unbookmark_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove bookmark from a post"""
    result = await db.execute(
        select(UserBookmark).where(
            and_(
                UserBookmark.post_id == post_id,
                UserBookmark.user_id == current_user.id
            )
        )
    )
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu post kaydedilmemiş"
        )
    
    await db.delete(bookmark)
    await db.commit()
    
    return SuccessResponse(message="Kayıt kaldırıldı")


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get comments for a post"""
    offset = (page - 1) * per_page
    
    result = await db.execute(
        select(PostComment)
        .options(selectinload(PostComment.user))
        .where(
            and_(
                PostComment.post_id == post_id,
                PostComment.parent_id.is_(None),
                PostComment.deleted_at.is_(None)
            )
        )
        .order_by(desc(PostComment.created_at))
        .offset(offset)
        .limit(per_page)
    )
    comments = result.scalars().all()
    
    return [
        CommentResponse(
            id=c.id,
            user=_build_comment_author(c.user),
            text=c.text,
            likes_count=c.likes_count,
            is_liked=False,  # TODO: Check if current user liked
            parent_id=c.parent_id,
            replies_count=0,  # TODO: Get actual count
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a comment on a post"""
    # Get post
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(
            and_(
                Post.id == post_id,
                Post.deleted_at.is_(None)
            )
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    if not post.author.allow_comments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu postta yorumlar kapalı"
        )
    
    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        text=data.text,
    )
    db.add(comment)
    
    post.comments_count += 1
    
    await db.commit()
    await db.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        user=_build_comment_author(current_user),
        text=comment.text,
        likes_count=0,
        is_liked=False,
        parent_id=comment.parent_id,
        replies_count=0,
        created_at=comment.created_at,
    )
