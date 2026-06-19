#!/usr/bin/env bash
# Canlı para motoru uçtan uca testi. Test hesapları gerektirir.
# Kullanım: BASE=https://31.57.187.149 PASS=Sifre123 bash scripts/test_money_flow.sh
set -uo pipefail

BASE="${BASE:-https://31.57.187.149}"
API="$BASE/api/v1"
PASS="${PASS:-Sifre123}"
CURL="curl -sk"

login() { $CURL -X POST "$API/auth/login" -H "Content-Type: application/json" -d "{\"username\":\"$1\",\"password\":\"$PASS\"}" | jq -r '.access_token // empty'; }
me_id() { $CURL "$API/users/me" -H "Authorization: Bearer $1" | jq -r '.id // empty'; }
bal()  { $CURL "$API/wallet/" -H "Authorization: Bearer $1" | jq -r '.balance'; }
earned() { $CURL "$API/wallet/" -H "Authorization: Bearer $1" | jq -r '.total_earned'; }

echo "== Giriş =="
ADMIN=$(login admin); FAN=$(login testfan); CREATOR=$(login testcreator)
echo "admin token: ${ADMIN:0:12}... | fan: ${FAN:0:12}... | creator: ${CREATOR:0:12}..."
[ -z "$ADMIN" ] && { echo "ADMIN login FAIL"; exit 1; }

CREATOR_ID=$(me_id "$CREATOR"); FAN_ID=$(me_id "$FAN")
echo "creator_id=$CREATOR_ID fan_id=$FAN_ID"

echo "== Başlangıç bakiyeleri =="
FAN_B0=$(bal "$FAN"); CRE_B0=$(bal "$CREATOR"); CRE_E0=$(earned "$CREATOR")
echo "fan=$FAN_B0 creator=$CRE_B0 creator_earned=$CRE_E0"

echo "== Admin kredi: fan +500 =="
$CURL -X POST "$API/admin/credit" -H "Authorization: Bearer $ADMIN" -H "Content-Type: application/json" \
  -d '{"username":"testfan","amount":500,"note":"test"}' | jq -c '.' 
FAN_B1=$(bal "$FAN"); echo "fan bakiye: $FAN_B0 -> $FAN_B1"

echo "== Tip: fan -> creator 100 TL (cüzdan) =="
$CURL -X POST "$API/payments/tip" -H "Authorization: Bearer $FAN" -H "Content-Type: application/json" \
  -d "{\"recipient_id\":\"$CREATOR_ID\",\"amount\":100,\"payment_method\":\"wallet\",\"message\":\"test tip\"}" | jq -c '{status,amount_usd}'
FAN_B2=$(bal "$FAN"); CRE_B2=$(bal "$CREATOR"); CRE_E2=$(earned "$CREATOR")
echo "fan: $FAN_B1 -> $FAN_B2 (beklenen -100)"
echo "creator: $CRE_B0 -> $CRE_B2 ; earned: $CRE_E0 -> $CRE_E2 (komisyon sonrası net artmalı)"

echo "== Escrow: fan 50 TL emanet -> creator teslim -> fan onay =="
ESC=$($CURL -X POST "$API/escrow" -H "Authorization: Bearer $FAN" -H "Content-Type: application/json" \
  -d '{"creator_username":"testcreator","title":"Test istek","description":"deneme","amount":50}')
echo "$ESC" | jq -c '{id,status,amount}'
ESC_ID=$(echo "$ESC" | jq -r '.id')
FAN_B3=$(bal "$FAN"); echo "fan escrow sonrası (hold): $FAN_B2 -> $FAN_B3 (beklenen -50)"
$CURL -X POST "$API/escrow/$ESC_ID/deliver" -H "Authorization: Bearer $CREATOR" -H "Content-Type: application/json" -d '{"note":"teslim","url":"https://x"}' | jq -c '{status}'
$CURL -X POST "$API/escrow/$ESC_ID/approve" -H "Authorization: Bearer $FAN" | jq -c '{status}'
CRE_B4=$(bal "$CREATOR"); echo "creator escrow onay sonrası: $CRE_B2 -> $CRE_B4 (komisyonlu +50 net)"

echo "== Withdrawal: creator 30 TL çekim talebi =="
$CURL -X POST "$API/wallet/withdraw" -H "Authorization: Bearer $CREATOR" -H "Content-Type: application/json" \
  -d '{"amount":30,"payment_method":"monero","payout_address":"46ggUJZKtN7BRWKMn2hvVh6QRNKvHheHniS2Ldcxhf8tZg8UkcLBj1geScCewdqZ71BMm4XvfPb7u3QgprMN6WiSHCnHckg"}' | jq -c '{id,amount,net_amount,status}'
CRE_B5=$(bal "$CREATOR"); echo "creator çekim talebi sonrası bakiye: $CRE_B4 -> $CRE_B5 (beklenen -30, pending'e)"

echo "== TEST BİTTİ =="
