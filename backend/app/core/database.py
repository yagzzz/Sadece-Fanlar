"""
Database connection and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables)"""
    from app.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()


async def _create_admin(
    username: str | None = None,
    password: str | None = None,
    email: str | None = None,
) -> None:
    """İlk yönetici (admin) hesabını oluşturur."""
    import os
    import secrets
    from sqlalchemy import select
    from app.core.security import hash_password
    from app.models.user import User, UserRole, UserStatus
    from app.models.transaction import Wallet

    username = (username or os.getenv("ADMIN_USERNAME", "admin")).lower()
    generated = False
    if not password:
        password = os.getenv("ADMIN_PASSWORD")
        if not password:
            password = secrets.token_urlsafe(16)
            generated = True

    # Tabloların var olduğundan emin ol
    await init_db()

    async with async_session_maker() as session:
        existing = await session.execute(select(User).where(User.username == username))
        if existing.scalar_one_or_none():
            print(f"Admin '{username}' zaten mevcut, atlanıyor.")
            return

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_email_verified=True,
            age_confirmed=True,
            display_name="Admin",
        )
        session.add(user)
        await session.flush()
        session.add(Wallet(user_id=user.id))
        await session.commit()

    print("=" * 50)
    print(f"Admin hesabı oluşturuldu: {username}")
    if generated:
        print(f"Geçici parola: {password}")
        print("Giriş yaptıktan sonra mutlaka parolanızı değiştirin.")
    print("=" * 50)


def create_admin(
    username: str | None = None,
    password: str | None = None,
    email: str | None = None,
) -> None:
    """
    Senkron sarmalayıcı (README'deki kullanım):
        python -c "from app.core.database import create_admin; create_admin()"

    Parola verilmezse ADMIN_PASSWORD env değişkeni kullanılır;
    o da yoksa güvenli rastgele bir parola üretilip ekrana yazılır.
    """
    import asyncio
    asyncio.run(_create_admin(username, password, email))
