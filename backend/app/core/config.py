"""
Application configuration
"""
from functools import lru_cache
from typing import List, Optional, Union
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App
    app_name: str = "Sadece Fanlar"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # API
    api_prefix: str = "/api"
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173"
    
    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        value = self.cors_origins_str
        if value.startswith("["):
            import json
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    
    # Database
    database_url: str = "postgresql+asyncpg://sadecefanlar:changeme@localhost:5432/sadecefanlar"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Auth
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    
    # Storage (MinIO/S3)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "sadecefanlar"
    minio_use_ssl: bool = False
    
    # BTCPay Server
    btcpay_url: str = "http://localhost:49392"
    btcpay_api_key: str = ""
    btcpay_store_id: str = ""
    btcpay_webhook_secret: str = ""
    
    # Monero
    monero_wallet_rpc_url: str = "http://localhost:18083"
    monero_wallet_rpc_user: str = "rpc_user"
    monero_wallet_rpc_password: str = "rpc_password"
    monero_wallet_name: str = "sadecefanlar"
    monero_confirmations_required: int = 10
    
    # Platform settings
    platform_fee_percent: float = 20.0  # 20% platform fee
    min_withdrawal_amount: float = 50.0
    max_withdrawal_amount: float = 10000.0
    referral_bonus_percent: float = 5.0
    
    # Media
    max_upload_size_mb: int = 500
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    allowed_video_types: List[str] = ["video/mp4", "video/webm", "video/quicktime"]
    allowed_audio_types: List[str] = ["audio/mpeg", "audio/wav", "audio/ogg"]
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()


settings = get_settings()
