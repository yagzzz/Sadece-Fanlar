"""
Sadece Fanlar - Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError
import logging

from app.core.config import settings
from app.core.database import engine

# Import all routers
from app.api.routes import (
    auth,
    users,
    posts,
    payments,
    subscriptions,
    messages,
    wallet,
    notifications,
    streams,
    admin,
    reports,
    tickets,
    escrow,
    ads,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    from sqlalchemy import text
    from app.core.redis import get_redis, close_redis
    
    # Startup
    logger.info("Starting Sadece Fanlar API...")
    logger.info(f"Environment: {settings.environment}")
    
    # Test database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    # Eksik tabloları oluştur. create_all yalnızca OLMAYAN tabloları ekler;
    # mevcut tabloları asla düşürmez/değiştirmez (production'da da güvenli).
    # Böylece yeni model eklendiğinde (ör. şipşak) tablo otomatik oluşur.
    if settings.auto_create_tables:
        try:
            from app.core.database import init_db
            await init_db()
            logger.info("Database tables ensured (auto_create_tables)")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
    
    # Test Redis connection
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sadece Fanlar API...")
    await engine.dispose()
    await close_redis()


# Create FastAPI application
app = FastAPI(
    title="Sadece Fanlar API",
    description="Anonim içerik platformu API - Monero & Bitcoin ödemeleri ile",
    version="1.0.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    openapi_url="/api/openapi.json" if settings.environment != "production" else None,
    lifespan=lifespan,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Güvenlik başlıkları ekler (clickjacking, MIME sniffing, bilgi sızıntısı vb.).
    Adds hardening HTTP headers to every response.
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        # Sunucu/teknoloji bilgisini gizle (parmak izini zorlaştırır).
        response.headers["Server"] = "sf"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)


# CORS middleware - yalnızca yapılandırılmış origin'lere ve gerekli method/header'lara izin ver.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    max_age=600,
)


# Exception handlers
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Bu kayıt zaten mevcut veya geçersiz veri"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.environment == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Bir hata oluştu. Lütfen daha sonra tekrar deneyin."}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "Sadece Fanlar API",
        "version": "1.0.0",
        "description": "Anonim içerik platformu - Kripto ödemeler ile",
        "payment_methods": ["Monero (XMR)", "Bitcoin (BTC/Lightning)"],
        "features": [
            "Anonim kayıt ve ödeme",
            "İçerik üreticileri için abonelik sistemi",
            "PPV (Ödeme-per-görüntüleme) içerikler",
            "Canlı yayın",
            "Özel mesajlaşma",
            "Kripto para çekimleri",
        ],
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(wallet.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(streams.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(escrow.router, prefix="/api/v1")
app.include_router(ads.router, prefix="/api/v1")


# SEO endpoints
@app.get("/robots.txt")
async def robots_txt():
    """
    Robots.txt - sadece tanıtım sayfaları indekslenebilir.
    Profil, içerik, ödeme ve hesap sayfaları gizlilik için indekslenmez.
    """
    content = """User-agent: *
Allow: /$
Allow: /explore
Allow: /register
Allow: /login
Disallow: /api/
Disallow: /admin/
Disallow: /messages/
Disallow: /settings/
Disallow: /wallet/
Disallow: /new-post
Disallow: /notifications
"""
    return JSONResponse(content=content, media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap():
    """Generate sitemap"""
    # TODO: Generate dynamic sitemap with public profiles
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://sadecefanlar.com/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://sadecefanlar.com/explore</loc>
        <changefreq>hourly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://sadecefanlar.com/register</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>
"""
    return JSONResponse(content=content, media_type="application/xml")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        workers=4 if settings.environment == "production" else 1,
    )
