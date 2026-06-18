"""
User API routes
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models.user import User, UserVerification, VerificationStatus
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.content import UserList, UserListMember, ListType
from app.schemas.user import (
    UserResponse,
    UserProfileResponse,
    UserUpdate,
    UserSearchResult,
    BecomeCreatorRequest,
)
from app.schemas.common import SuccessResponse, PaginatedResponse
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/me/flag-screenshot")
async def flag_screenshot(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    İstemci ekran görüntüsü girişimi algıladığında çağrılır.
    Hesabı askıya alır (web'de %100 engellenemez; bu caydırıcı + iz mekanizmasıdır).
    """
    from app.models.user import UserStatus
    current_user.status = UserStatus.SUSPENDED
    current_user.ban_reason = "Ekran görüntüsü/izinsiz kayıt girişimi"
    await db.commit()
    return {"status": "suspended"}


@router.post("/creator-application", response_model=UserResponse)
async def creator_application(
    data: BecomeCreatorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    İçerik Üreticisi Başvurusu (Gizlilik Öncelikli)
    -----------------------------------------------
    Kayıtlı kullanıcıyı içerik üreticisine dönüştürür.

    GİZLİLİK: Gerçek isim, kimlik belgesi veya yüz fotoğrafı TOPLANMAZ.
    Sadece takma ad (display_name), tanıtım ve 18+ yaş beyanı yeterlidir.
    """
    if current_user.is_creator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten bir içerik üreticisisiniz",
        )

    current_user.is_creator = True
    current_user.age_confirmed = True
    current_user.display_name = data.display_name or current_user.display_name
    current_user.bio = data.bio
    current_user.subscription_price = data.subscription_price

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's full profile"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload profile avatar"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece resim dosyaları yüklenebilir"
        )
    
    # TODO: Upload to MinIO and get URL
    from app.services.storage import upload_file
    url = await upload_file(file, f"avatars/{current_user.id}")
    
    current_user.avatar_url = url
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/cover", response_model=UserResponse)
async def upload_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload profile cover image"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece resim dosyaları yüklenebilir"
        )
    
    from app.services.storage import upload_file
    url = await upload_file(file, f"covers/{current_user.id}")
    
    current_user.cover_url = url
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/become-creator", response_model=UserResponse)
async def become_creator(
    data: BecomeCreatorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request to become a content creator"""
    if current_user.is_creator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten bir içerik üreticisisiniz"
        )
    
    # Update user (18+ beyanı schema tarafından zorunlu kılınır)
    current_user.is_creator = True
    current_user.age_confirmed = True
    current_user.display_name = data.display_name
    current_user.bio = data.bio
    current_user.subscription_price = data.subscription_price
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


async def get_user_profile(
    username: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get a user's public profile"""
    result = await db.execute(
        select(User).where(
            and_(
                User.username == username.lower(),
                User.deleted_at.is_(None)
            )
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Check if current user is subscribed
    is_subscribed = False
    is_following = False
    
    if current_user:
        # Check subscription
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.subscriber_id == current_user.id,
                    Subscription.creator_id == user.id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        is_subscribed = result.scalar_one_or_none() is not None
        
        # Check if following (in any list)
        result = await db.execute(
            select(UserListMember).join(UserList).where(
                and_(
                    UserList.user_id == current_user.id,
                    UserList.type == ListType.FOLLOWING,
                    UserListMember.member_id == user.id
                )
            )
        )
        is_following = result.scalar_one_or_none() is not None
    
    # Build response
    response = UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        location=user.location,
        website=user.website,
        avatar_url=user.avatar_url,
        cover_url=user.cover_url,
        is_creator=user.is_creator,
        is_verified_creator=user.is_verified_creator,
        is_free_profile=user.is_free_profile,
        subscription_price=user.subscription_price,
        subscription_price_3m=user.subscription_price_3m,
        subscription_price_6m=user.subscription_price_6m,
        subscription_price_12m=user.subscription_price_12m,
        posts_count=user.posts_count,
        subscribers_count=user.subscribers_count if user.show_subscribers_count else None,
        likes_count=user.likes_count,
        is_subscribed=is_subscribed,
        is_following=is_following,
        created_at=user.created_at,
    )
    
    return response


@router.get("/search", response_model=list[UserSearchResult])
async def search_users(
    q: str = Query(..., min_length=2, max_length=50),
    limit: int = Query(default=20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Search for users"""
    search_term = f"%{q.lower()}%"
    
    result = await db.execute(
        select(User)
        .where(
            and_(
                User.deleted_at.is_(None),
                User.is_active == True,
                func.lower(User.username).like(search_term) |
                func.lower(User.display_name).like(search_term)
            )
        )
        .order_by(User.subscribers_count.desc())
        .limit(limit)
    )
    
    users = result.scalars().all()
    return users


@router.get("/creators")
async def list_creators(
    sort: str = Query(default="featured"),
    q: Optional[str] = Query(default=None, max_length=50),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    İçerik üreticilerini listele (Keşfet sayfası).
    sort: featured | new | popular
    Arama (q) opsiyoneldir; boşsa tüm üreticiler döner.
    """
    offset = (page - 1) * limit

    filters = [
        User.deleted_at.is_(None),
        User.is_active == True,
        User.is_creator == True,
    ]

    if q:
        term = f"%{q.lower()}%"
        filters.append(
            func.lower(User.username).like(term) | func.lower(User.display_name).like(term)
        )

    query = select(User).where(and_(*filters))

    if sort == "new":
        query = query.order_by(User.created_at.desc())
    elif sort == "popular":
        query = query.order_by(User.subscribers_count.desc(), User.posts_count.desc())
    else:  # featured
        query = query.order_by(
            User.is_verified_creator.desc(),
            User.subscribers_count.desc(),
        )

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    creators = result.scalars().all()

    total = await db.scalar(select(func.count(User.id)).where(and_(*filters))) or 0

    return {
        "items": [UserSearchResult.model_validate(u) for u in creators],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": offset + len(creators) < total,
    }


@router.post("/{username}/follow", response_model=SuccessResponse)
async def follow_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow a user (add to following list)"""
    # Get target user
    result = await db.execute(
        select(User).where(User.username == username.lower())
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinizi takip edemezsiniz"
        )
    
    # Get or create following list
    result = await db.execute(
        select(UserList).where(
            and_(
                UserList.user_id == current_user.id,
                UserList.type == ListType.FOLLOWING
            )
        )
    )
    following_list = result.scalar_one_or_none()
    
    if not following_list:
        following_list = UserList(
            user_id=current_user.id,
            name="Following",
            type=ListType.FOLLOWING,
        )
        db.add(following_list)
        await db.flush()
    
    # Check if already following
    result = await db.execute(
        select(UserListMember).where(
            and_(
                UserListMember.list_id == following_list.id,
                UserListMember.member_id == target_user.id
            )
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten takip ediyorsunuz"
        )
    
    # Add to list
    member = UserListMember(
        list_id=following_list.id,
        member_id=target_user.id,
    )
    db.add(member)
    following_list.members_count += 1
    
    await db.commit()
    
    return SuccessResponse(message="Takip edildi")


@router.delete("/{username}/follow", response_model=SuccessResponse)
async def unfollow_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unfollow a user"""
    # Get target user
    result = await db.execute(
        select(User).where(User.username == username.lower())
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Get following list
    result = await db.execute(
        select(UserList).where(
            and_(
                UserList.user_id == current_user.id,
                UserList.type == ListType.FOLLOWING
            )
        )
    )
    following_list = result.scalar_one_or_none()
    
    if not following_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten takip etmiyorsunuz"
        )
    
    # Remove from list
    result = await db.execute(
        select(UserListMember).where(
            and_(
                UserListMember.list_id == following_list.id,
                UserListMember.member_id == target_user.id
            )
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zaten takip etmiyorsunuz"
        )
    
    await db.delete(member)
    following_list.members_count -= 1
    
    await db.commit()
    
    return SuccessResponse(message="Takip bırakıldı")


# Dinamik "/{username}" rotası EN SONA kaydedilir; aksi halde "/search",
# "/creator-application" gibi statik rotaları gölgeler (yakalar).
router.add_api_route(
    "/{username}",
    get_user_profile,
    methods=["GET"],
    response_model=UserProfileResponse,
    tags=["Users"],
)
