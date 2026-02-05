# Sadece Fanlar - Backend API

Python FastAPI backend for the content subscription platform.

## Features

- User authentication (JWT + 2FA)
- Content management (posts, media, stories)
- Subscription system
- Crypto payments (Monero, BTCPay Server)
- Real-time messaging (WebSocket)
- Live streaming support
- Admin panel API

## Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy
- Redis + Celery
- MinIO (S3-compatible storage)
- FFmpeg (media processing)

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```
