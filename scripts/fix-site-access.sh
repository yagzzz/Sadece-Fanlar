#!/usr/bin/env bash
# Site 502 / erişim sorunlarını giderir. Sunucuda root olarak çalıştırın:
#   cd /opt/sadece-fanlar && bash scripts/fix-site-access.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/sadece-fanlar}"
BRANCH="${BRANCH:-main}"

cd "$APP_DIR"

echo "==> Son kod çekiliyor ($BRANCH)"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

echo "==> Frontend yeniden build + başlat"
export PUBLIC_API_URL="${PUBLIC_API_URL:-https://31.57.187.149}"
export PUBLIC_WS_URL="${PUBLIC_WS_URL:-wss://31.57.187.149}"
export ORIGIN="${ORIGIN:-https://31.57.187.149}"

docker compose build --build-arg PUBLIC_API_URL="$PUBLIC_API_URL" \
  --build-arg PUBLIC_WS_URL="$PUBLIC_WS_URL" frontend
docker compose up -d frontend

echo "==> Frontend sağlık bekleniyor..."
for i in $(seq 1 30); do
  if docker compose exec -T frontend wget -q -O /dev/null http://127.0.0.1:3000/ 2>/dev/null; then
    echo "Frontend hazır."
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "HATA: Frontend ayağa kalkmadı. Loglar:"
    docker compose logs frontend --tail 40
    exit 1
  fi
  sleep 2
done

echo "==> Nginx yeniden başlatılıyor (upstream IP yenilensin)"
docker compose up -d nginx
docker compose restart nginx

echo "==> Kontrol"
sleep 3
curl -sf http://127.0.0.1:3000/ >/dev/null && echo "OK: frontend :3000"
curl -sk -o /dev/null -w "HTTPS ana sayfa: %{http_code}\n" https://127.0.0.1/ || true
docker compose ps

echo ""
echo "Site: https://31.57.187.149"
echo "Self-signed SSL uyarısında 'Gelişmiş' → devam edin."
