"""
Site ayarları — key-value settings tablosu üzerinden platform yapılandırması.
"""
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.models.admin import Setting

SETTING_DEFAULTS: Dict[str, Any] = {
    "site_name": "Sadece Fanlar",
    "site_description": "Anonim içerik üretici platformu",
    "platform_fee_percent": app_settings.platform_fee_percent,
    "withdrawal_fee_percent": app_settings.withdrawal_fee_percent,
    "min_withdrawal_amount": app_settings.min_withdrawal_amount,
    "min_subscription_price": 1.0,
    "max_subscription_price": 500.0,
    "maintenance_mode": False,
    "registration_enabled": True,
    "creator_verification_required": False,
    "monero_enabled": True,
    "btcpay_enabled": True,
    "referral_bonus_percent": app_settings.referral_bonus_percent,
    "max_upload_size_mb": app_settings.max_upload_size_mb,
    "signup_bonus_try": app_settings.signup_bonus_try,
}

SETTING_TYPES: Dict[str, str] = {
    "site_name": "string",
    "site_description": "string",
    "platform_fee_percent": "number",
    "withdrawal_fee_percent": "number",
    "min_withdrawal_amount": "number",
    "min_subscription_price": "number",
    "max_subscription_price": "number",
    "maintenance_mode": "boolean",
    "registration_enabled": "boolean",
    "creator_verification_required": "boolean",
    "monero_enabled": "boolean",
    "btcpay_enabled": "boolean",
    "referral_bonus_percent": "number",
    "max_upload_size_mb": "number",
    "signup_bonus_try": "number",
}


def _cast_value(key: str, raw: Optional[str]) -> Any:
    if raw is None:
        return SETTING_DEFAULTS.get(key)
    typ = SETTING_TYPES.get(key, "string")
    if typ == "boolean":
        return raw.lower() in ("1", "true", "yes", "on")
    if typ == "number":
        return float(Decimal(raw))
    return raw


def _serialize_value(key: str, value: Any) -> str:
    typ = SETTING_TYPES.get(key, "string")
    if typ == "boolean":
        return "true" if value else "false"
    return str(value)


async def get_platform_settings(db: AsyncSession) -> Dict[str, Any]:
    result = await db.execute(select(Setting).where(Setting.key.in_(SETTING_DEFAULTS.keys())))
    stored = {row.key: row.value for row in result.scalars()}
    out = dict(SETTING_DEFAULTS)
    for key in SETTING_DEFAULTS:
        if key in stored:
            out[key] = _cast_value(key, stored[key])
    return out


async def get_setting(db: AsyncSession, key: str, default: Any = None) -> Any:
    """Tek bir ayarı getirir (yoksa varsayılan)."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    row = result.scalar_one_or_none()
    if row is None:
        return SETTING_DEFAULTS.get(key, default)
    return _cast_value(key, row.value)


async def get_fee_percent(db: AsyncSession) -> float:
    """Geçerli platform komisyon yüzdesi (admin ayarından)."""
    return float(await get_setting(db, "platform_fee_percent"))


async def update_platform_settings(db: AsyncSession, updates: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in updates.items():
        if key not in SETTING_DEFAULTS or value is None:
            continue
        result = await db.execute(select(Setting).where(Setting.key == key))
        row = result.scalar_one_or_none()
        serialized = _serialize_value(key, value)
        if row:
            row.value = serialized
            row.type = SETTING_TYPES.get(key, "string")
        else:
            db.add(
                Setting(
                    key=key,
                    value=serialized,
                    type=SETTING_TYPES.get(key, "string"),
                    group="platform",
                )
            )
    await db.commit()
    return await get_platform_settings(db)
