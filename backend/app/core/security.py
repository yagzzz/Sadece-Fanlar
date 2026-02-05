"""
Security utilities - JWT, password hashing, 2FA
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import hashlib

from jose import jwt, JWTError
from passlib.context import CryptContext
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


# JWT tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def create_tokens(user_id: str, username: str) -> Tuple[str, str]:
    """Create both access and refresh tokens"""
    data = {"sub": user_id, "username": username}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    return access_token, refresh_token


# 2FA (TOTP)
def generate_2fa_secret() -> str:
    """Generate a new 2FA secret"""
    return pyotp.random_base32()


def get_2fa_uri(secret: str, username: str) -> str:
    """Get TOTP URI for QR code"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=settings.app_name)


def generate_2fa_qr_code(secret: str, username: str) -> str:
    """Generate QR code for 2FA setup as base64 PNG"""
    uri = get_2fa_uri(secret, username)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, "PNG")
    
    return base64.b64encode(buffer.getvalue()).decode()


def verify_2fa_code(secret: str, code: str) -> bool:
    """Verify a 2FA code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 30 second window


# Token hashing (for storing refresh tokens)
def hash_token(token: str) -> str:
    """Hash a token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


# Generate secure random strings
def generate_random_string(length: int = 32) -> str:
    """Generate a secure random string"""
    return secrets.token_urlsafe(length)


def generate_referral_code() -> str:
    """Generate a referral code"""
    return secrets.token_urlsafe(8).upper()[:10]


def generate_stream_key() -> str:
    """Generate a stream key"""
    return secrets.token_urlsafe(32)
