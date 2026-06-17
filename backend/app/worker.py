"""
Celery Worker - Arka Plan İşleri
================================
docker-compose bu modülü `celery -A app.worker ...` ile çalıştırır.

Görevler:
- Süresi dolan ödeme isteklerini kapatma
- Süresi dolan abonelikleri pasifleştirme
- (Medya kuyruğu) ağır medya işleme görevleri için altyapı

Not: Uygulama async (asyncpg) kullandığından, Celery görevleri içinde
async fonksiyonlar `asyncio.run` ile çalıştırılır.
"""
import asyncio
import logging
from datetime import datetime

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "sadecefanlar",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    worker_max_tasks_per_child=200,
    broker_connection_retry_on_startup=True,
)

# Periyodik görevler (celery beat)
celery_app.conf.beat_schedule = {
    "expire-payment-requests": {
        "task": "app.worker.expire_payment_requests",
        "schedule": 300.0,  # 5 dakikada bir
    },
    "expire-subscriptions": {
        "task": "app.worker.expire_subscriptions",
        "schedule": 600.0,  # 10 dakikada bir
    },
}

# `-A app.worker` farklı isimler altında uygulamayı bulabilsin diye alias'lar.
celery = celery_app
app = celery_app


def _run(coro):
    """Senkron Celery görevi içinde async fonksiyon çalıştırır."""
    return asyncio.run(coro)


@celery_app.task(name="app.worker.health_ping")
def health_ping() -> str:
    """Worker'ın çalıştığını doğrulamak için basit görev."""
    return "ok"


@celery_app.task(name="app.worker.expire_payment_requests")
def expire_payment_requests() -> int:
    """Süresi dolmuş bekleyen ödeme isteklerini EXPIRED yapar."""
    return _run(_expire_payment_requests())


async def _expire_payment_requests() -> int:
    from sqlalchemy import update
    from app.core.database import async_session_maker
    from app.models.payment import PaymentRequest, PaymentRequestStatus

    async with async_session_maker() as session:
        result = await session.execute(
            update(PaymentRequest)
            .where(
                PaymentRequest.status.in_(
                    [PaymentRequestStatus.PENDING, PaymentRequestStatus.AWAITING_PAYMENT]
                ),
                PaymentRequest.expires_at < datetime.utcnow(),
            )
            .values(status=PaymentRequestStatus.EXPIRED)
        )
        await session.commit()
        count = result.rowcount or 0
        if count:
            logger.info("Expired %s payment requests", count)
        return count


@celery_app.task(name="app.worker.expire_subscriptions")
def expire_subscriptions() -> int:
    """Süresi dolmuş aktif abonelikleri EXPIRED yapar."""
    return _run(_expire_subscriptions())


async def _expire_subscriptions() -> int:
    from sqlalchemy import update
    from app.core.database import async_session_maker
    from app.models.subscription import Subscription, SubscriptionStatus

    async with async_session_maker() as session:
        result = await session.execute(
            update(Subscription)
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.expires_at < datetime.utcnow(),
            )
            .values(status=SubscriptionStatus.EXPIRED)
        )
        await session.commit()
        count = result.rowcount or 0
        if count:
            logger.info("Expired %s subscriptions", count)
        return count
