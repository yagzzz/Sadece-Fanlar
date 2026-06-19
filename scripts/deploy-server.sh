#!/usr/bin/env bash
set -euo pipefail

# Sadece Fanlar - tek komut sunucu kurulumu
# Kullanım: SERVER_IP=1.2.3.4 bash scripts/deploy-server.sh

SERVER_IP="${SERVER_IP:-31.57.187.149}"
APP_DIR="/opt/sadece-fanlar"
BRANCH="${BRANCH:-main}"
REPO="https://github.com/yagzzz/Sadece-Fanlar.git"

echo "==> Docker kurulumu"
if ! command -v docker >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl git openssl ufw
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | tee /etc/apt/sources.list.d/docker.list >/dev/null
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
fi

echo "==> Repo"
mkdir -p /opt
if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR"
  git fetch origin
  git checkout "$BRANCH"
  git pull origin "$BRANCH"
else
  git clone --branch "$BRANCH" "$REPO" "$APP_DIR"
  cd "$APP_DIR"
fi

echo "==> Geliştirme volume mount'ları kaldırılıyor (production)"
sed -i '/- \.\/backend:\/app/d' docker-compose.yml
sed -i '/- \.\/frontend:\/app/d' docker-compose.yml
sed -i '/- \/app\/node_modules/d' docker-compose.yml
sed -i '/- \.\/backend:\/app/d' docker-compose.yml 2>/dev/null || true

echo "==> Redis healthcheck düzeltmesi"
python3 - <<'PY'
from pathlib import Path
p = Path("docker-compose.yml")
text = p.read_text()
old = '      test: ["CMD", "redis-cli", "ping"]'
new = '      test: ["CMD-SHELL", "redis-cli -a \\"$REDIS_PASSWORD\\" ping | grep -q PONG"]'
if old in text:
    p.write_text(text.replace(old, new))
PY

echo "==> .env oluşturuluyor"
if [ ! -f .env ]; then
  SECRET=$(openssl rand -hex 32)
  DB_PASS=$(openssl rand -hex 24)
  REDIS_PASS=$(openssl rand -hex 24)
  MINIO_KEY=$(openssl rand -hex 16)
  MINIO_SECRET=$(openssl rand -hex 32)
  MONERO_RPC_PASS=$(openssl rand -hex 24)
  BTCPAY_WEBHOOK=$(openssl rand -hex 32)
  STREAM_SECRET=$(openssl rand -hex 32)

  cat > .env <<EOF
DB_PASSWORD=${DB_PASS}
REDIS_PASSWORD=${REDIS_PASS}
SECRET_KEY=${SECRET}
ENVIRONMENT=development
CORS_ORIGINS=https://${SERVER_IP},http://${SERVER_IP}
PUBLIC_API_URL=https://${SERVER_IP}
PUBLIC_WS_URL=wss://${SERVER_IP}
ORIGIN=https://${SERVER_IP}
BTCPAY_URL=http://btcpay:49392
BTCPAY_API_KEY=
BTCPAY_STORE_ID=
BTCPAY_WEBHOOK_SECRET=${BTCPAY_WEBHOOK}
BTCPAY_NETWORK=testnet
MONERO_WALLET_RPC_URL=http://monero-wallet:18083
MONERO_WALLET_RPC_USER=rpc_user
MONERO_WALLET_RPC_PASSWORD=${MONERO_RPC_PASS}
MONERO_DAEMON_HOST=node.community.rino.io
MONERO_DAEMON_PORT=18089
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_URL=https://${SERVER_IP}/media
MINIO_ACCESS_KEY=${MINIO_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET}
MINIO_BUCKET=sadecefanlar
STREAM_KEY_SECRET=${STREAM_SECRET}
EOF
  chmod 600 .env
else
  echo ".env zaten var, dokunulmadı"
fi

echo "==> SSL (self-signed, IP için)"
mkdir -p nginx/ssl
if [ ! -f nginx/ssl/cert.pem ]; then
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/CN=${SERVER_IP}"
fi

echo "==> Firewall"
ufw allow 22/tcp >/dev/null 2>&1 || true
ufw allow 80/tcp >/dev/null 2>&1 || true
ufw allow 443/tcp >/dev/null 2>&1 || true
ufw --force enable >/dev/null 2>&1 || true

echo "==> Docker build & start"
export PUBLIC_API_URL="https://${SERVER_IP}"
export PUBLIC_WS_URL="wss://${SERVER_IP}"
export ORIGIN="https://${SERVER_IP}"

# BTCPay ağır ve ayrı kurulum gerektirir; önce çekirdek stack
docker compose build --build-arg PUBLIC_API_URL="https://${SERVER_IP}" --build-arg PUBLIC_WS_URL="wss://${SERVER_IP}" backend frontend
docker compose up -d postgres redis minio backend frontend nginx celery_worker celery_beat monero-wallet

echo "==> Servislerin ayağa kalkması bekleniyor..."
sleep 15

echo "==> Sağlık kontrolü"
curl -sf http://127.0.0.1:8000/health || docker compose logs backend --tail 30

echo "==> Nginx/frontend senkron (502 önleme)"
bash scripts/fix-site-access.sh

echo ""
echo "============================================"
echo " Kurulum tamamlandı!"
echo " Site: https://${SERVER_IP}"
echo " (Self-signed SSL - tarayıcıda 'gelişmiş' ile devam et)"
echo "============================================"
