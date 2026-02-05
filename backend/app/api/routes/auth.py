"""
Kimlik Doğrulama API Rotaları
=============================
Bu dosya kullanıcı kimlik doğrulama ile ilgili API endpoint'lerini içerir.

Endpoint'ler:
- POST /auth/register: Yeni kullanıcı kaydı
- POST /auth/login: Kullanıcı girişi
- POST /auth/logout: Çıkış
- POST /auth/refresh: Token yenileme
- POST /auth/2fa/setup: 2FA kurulumu
- POST /auth/2fa/verify: 2FA doğrulama
- POST /auth/password/change: Şifre değiştirme
- POST /auth/password/reset: Şifre sıfırlama
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_tokens,
    decode_token,
    generate_2fa_secret,
    verify_2fa_code,
    generate_2fa_qr_code,
    generate_referral_code,
    hash_token,
)
from app.core.redis import Cache, RateLimiter
from app.models.user import User, UserSettings, UserDevice
from app.models.transaction import Wallet
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    TwoFactorSetup,
    TwoFactorVerify,
    ChangePassword,
)
from app.schemas.common import SuccessResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Yeni Kullanıcı Kaydı
    --------------------
    Yeni bir kullanıcı hesabı oluşturur.
    
    - Rate limit: IP başına saatte 5 deneme
    - Kullanıcı adı ve e-posta benzersiz olmalı
    - Referans kodu ile kayıt olunabilir
    - Otomatik olarak cüzdan ve ayarlar oluşturulur
    """
    # Rate limiting - Aşırı kayıt denemesini engelle
    client_ip = request.client.host if request.client else "unknown"
    if not await RateLimiter.is_allowed(f"register:{client_ip}", 5, 3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla kayıt denemesi. Lütfen 1 saat bekleyin."
        )
    
    # Kullanıcı adı kontrolü
    result = await db.execute(
        select(User).where(User.username == data.username.lower())
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kullanılıyor"
        )
    
    # E-posta kontrolü
    result = await db.execute(
        select(User).where(User.email == data.email.lower())
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kullanılıyor"
        )
    
    # Referans kodu kontrolü (varsa)
    referred_by = None
    if data.referral_code:
        result = await db.execute(
            select(User).where(User.referral_code == data.referral_code.upper())
        )
        referred_by = result.scalar_one_or_none()
        if not referred_by:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz referans kodu"
            )
    
    # Kullanıcı oluştur
    user = User(
        username=data.username.lower(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        display_name=data.display_name or data.username,
        referral_code=generate_referral_code(),
        referred_by_id=referred_by.id if referred_by else None,
    )
    db.add(user)
    await db.flush()
    
    # Cüzdan oluştur (her kullanıcının bir cüzdanı var)
    wallet = Wallet(user_id=user.id)
    db.add(wallet)
    
    # Kullanıcı ayarları oluştur
    settings = UserSettings(user_id=user.id)
    db.add(settings)
    
    await db.commit()
    await db.refresh(user)
    
    # JWT token'ları oluştur
    access_token, refresh_token = create_tokens(str(user.id), user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Kullanıcı Girişi
    ----------------
    Kullanıcı adı/e-posta ve şifre ile giriş yapar.
    
    - Rate limit: IP başına 5 dakikada 10 deneme
    - 2FA etkinse kod gerekir
    - Başarılı girişte JWT token döner
    """
    # Rate limiting - Brute force saldırısını engelle
    client_ip = request.client.host if request.client else "unknown"
    if not await RateLimiter.is_allowed(f"login:{client_ip}", 10, 300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla giriş denemesi. Lütfen 5 dakika bekleyin."
        )
    
    # Kullanıcıyı bul (kullanıcı adı veya e-posta ile)
    result = await db.execute(
        select(User).where(
            or_(
                User.username == data.username.lower(),
                User.email == data.username.lower()
            )
        )
    )
    user = result.scalar_one_or_none()
    
    # Şifre doğrulama
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız devre dışı bırakılmış"
        )
    
    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız silinmiş"
        )
    
    # Check 2FA
    if user.two_factor_enabled:
        if not data.two_factor_code:
            return TokenResponse(
                access_token="",
                refresh_token="",
                requires_2fa=True,
            )
        
        if not user.two_factor_secret:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA aktif değil")
        if not verify_2fa_code(user.two_factor_secret, data.two_factor_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz 2FA kodu"
            )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    user.last_active_at = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token, refresh_token = create_tokens(str(user.id), user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    payload = decode_token(data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı veya devre dışı"
        )
    
    # Create new tokens
    access_token, refresh_token = create_tokens(str(user.id), user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout (invalidate tokens)"""
    # In a production system, you might want to blacklist the token
    # For now, we just return success (client should delete tokens)
    return SuccessResponse(message="Çıkış yapıldı")


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup 2FA for the user"""
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA zaten etkin"
        )
    
    # Generate secret
    secret = generate_2fa_secret()
    qr_code = generate_2fa_qr_code(secret, current_user.username)
    
    # Store secret temporarily (will be confirmed on verify)
    await Cache.set(f"2fa_setup:{current_user.id}", secret, expire=600)
    
    # Generate backup codes
    from app.core.security import generate_random_string
    backup_codes = [generate_random_string(8) for _ in range(10)]
    await Cache.set(f"2fa_backup:{current_user.id}", backup_codes, expire=600)
    
    return TwoFactorSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes,
    )


@router.post("/2fa/verify", response_model=SuccessResponse)
async def verify_2fa_setup(
    data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify and enable 2FA"""
    # Get stored secret
    secret = await Cache.get(f"2fa_setup:{current_user.id}")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA kurulumu bulunamadı. Lütfen tekrar deneyin."
        )
    
    # Verify code
    if not verify_2fa_code(secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz doğrulama kodu"
        )
    
    # Enable 2FA
    current_user.two_factor_enabled = True
    current_user.two_factor_secret = secret
    await db.commit()
    
    # Clear temporary data
    await Cache.delete(f"2fa_setup:{current_user.id}")
    
    return SuccessResponse(message="2FA başarıyla etkinleştirildi")


@router.post("/2fa/disable", response_model=SuccessResponse)
async def disable_2fa(
    data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable 2FA"""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA zaten devre dışı"
        )
    
    # Verify code
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA aktif değil")
    if not verify_2fa_code(current_user.two_factor_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz doğrulama kodu"
        )
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    await db.commit()
    
    return SuccessResponse(message="2FA devre dışı bırakıldı")


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password"""
    # Verify current password
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mevcut şifre hatalı"
        )
    
    # Update password
    current_user.password_hash = hash_password(data.new_password)
    await db.commit()
    
    return SuccessResponse(message="Şifreniz başarıyla değiştirildi")
