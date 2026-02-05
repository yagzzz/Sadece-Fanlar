# SadeceFanlar - Anonim İçerik Üretici Platformu

🔒 **Privacy-first** içerik üretici platformu - Monero ve Bitcoin ile anonim ödemeler

## Özellikler

### 🎨 Modern Arayüz
- SvelteKit + TailwindCSS ile modern, responsive tasarım
- Dark mode desteği
- PWA desteği (mobil uygulamaya gerek yok)

### 💰 Anonim Ödeme Sistemi
- **Monero (XMR)** - Tam anonim ödemeler
- **Bitcoin (BTC)** - BTCPay Server ile self-hosted
- Hiçbir kişisel veri gerekmez

### 📱 Temel Özellikler
- Abonelik sistemi (aylık/bundle)
- PPV (Pay-per-view) içerikler
- Mesajlaşma (WebSocket ile gerçek zamanlı)
- Bahşiş sistemi
- Canlı yayın desteği (RTMP)
- Bildirimler (gerçek zamanlı)
- Referral sistemi
- Admin paneli

### 🛡️ Güvenlik
- JWT tabanlı kimlik doğrulama
- 2FA desteği (TOTP)
- Rate limiting
- Şifreli depolama

## Teknoloji Stack

### Backend
- Python 3.11+
- FastAPI (async)
- PostgreSQL 15
- Redis 7
- Celery (arka plan işleri)
- MinIO (S3-uyumlu depolama)

### Frontend
- SvelteKit
- TailwindCSS
- TypeScript

### Altyapı
- Docker & Docker Compose
- Nginx (reverse proxy)
- BTCPay Server
- Monero wallet-rpc

## Kurulum

### Gereksinimler
- Docker & Docker Compose
- Git
- Domain (SSL için)

### Hızlı Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/your-repo/sadece-fanlar.git
cd sadece-fanlar
```

2. Environment dosyasını oluşturun:
```bash
cp .env.example .env
nano .env  # Ayarları düzenleyin
```

3. Docker ile başlatın:
```bash
docker-compose up -d
```

4. Database migration:
```bash
docker-compose exec backend alembic upgrade head
```

5. Admin kullanıcı oluşturun:
```bash
docker-compose exec backend python -c "from app.core.database import create_admin; create_admin()"
```

### Erişim

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **BTCPay Server**: http://localhost:23000
- **MinIO Console**: http://localhost:9001

## Yapılandırma

### .env Değişkenleri

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/sadecefanlar

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monero
MONERO_WALLET_RPC_URL=http://monero-wallet:18082
MONERO_WALLET_PASSWORD=wallet-password

# BTCPay
BTCPAY_URL=http://btcpay:23000
BTCPAY_STORE_ID=your-store-id
BTCPAY_API_KEY=your-api-key

# Storage (MinIO)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=sadecefanlar

# Platform Settings
PLATFORM_FEE_PERCENT=20
MIN_WITHDRAWAL=10.00
```

### BTCPay Server Kurulumu

1. BTCPay Server'a erişin: http://localhost:23000
2. Yeni store oluşturun
3. Bitcoin/Lightning wallet ekleyin
4. API key oluşturun
5. .env dosyasına ekleyin

### Monero Wallet Kurulumu

Monero wallet otomatik olarak Docker tarafından oluşturulur. İlk başlatmada:
```bash
docker-compose logs monero-wallet
```
ile wallet adresini görebilirsiniz.

## API Dokümantasyonu

API dokümantasyonuna `/docs` endpoint'inden erişebilirsiniz:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Temel Endpoint'ler

```
POST /api/v1/auth/register - Kayıt
POST /api/v1/auth/login - Giriş
GET  /api/v1/users/me - Profil
GET  /api/v1/posts - Post listesi
POST /api/v1/posts - Yeni post
GET  /api/v1/subscriptions - Abonelikler
POST /api/v1/payments/monero/deposit - Monero yatırma
POST /api/v1/payments/btcpay/invoice - Bitcoin ödeme
GET  /api/v1/wallet - Cüzdan bilgileri
```

## Geliştirme

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Yeni migration oluştur
alembic revision --autogenerate -m "migration_name"

# Migration'ları uygula
alembic upgrade head

# Geri al
alembic downgrade -1
```

## Güvenlik Notları

⚠️ **Production için**:
1. Tüm secret key'leri değiştirin
2. SSL sertifikası kullanın
3. Güvenlik duvarı kurallarını yapılandırın
4. Düzenli yedekleme yapın
5. Rate limiting'i production değerlerine ayarlayın

## Lisans

MIT License - Özgürce kullanabilir ve değiştirebilirsiniz.

## Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır. Büyük değişiklikler için önce issue açınız.

---

**SadeceFanlar** - Gizliliğinize saygı duyan içerik platformu 🔒
