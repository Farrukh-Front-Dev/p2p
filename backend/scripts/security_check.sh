#!/bin/bash
# Xavfsizlik tekshiruvi

BASE="http://localhost:8001"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          XAVFSIZLIK TEKSHIRUVI                          ║"
echo "╚══════════════════════════════════════════════════════════╝"

echo ""
echo "1. Admin panel himoyasi (login kerak)"
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/admin/")
if [ "$CODE" = "302" ]; then echo "   ✅ Admin → 302 redirect (login kerak)"; else echo "   ❌ Admin → $CODE"; fi

echo ""
echo "2. Admin login sahifasi"
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/admin/login")
if [ "$CODE" = "200" ]; then echo "   ✅ Login sahifasi mavjud"; else echo "   ❌ Login → $CODE"; fi

echo ""
echo "3. API auth guard (tokensiz)"
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/v1/auth/me")
if [ "$CODE" = "401" ]; then echo "   ✅ Tokensiz → 401"; else echo "   ❌ → $CODE"; fi

echo ""
echo "4. Admin API guard (tokensiz)"
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/v1/admin/users")
if [ "$CODE" = "401" ]; then echo "   ✅ Admin API tokensiz → 401"; else echo "   ❌ → $CODE"; fi

echo ""
echo "5. Rate limit (5 ta so'rov /school21/login)"
LAST="200"
for i in $(seq 1 7); do
  LAST=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/v1/auth/school21/login" \
    -H "Content-Type: application/json" -d '{"init_data":"hash=x","login":"x","password":"x"}')
done
if [ "$LAST" = "429" ]; then echo "   ✅ Rate limit ishlaydi (429)"; else echo "   ⚠️  Son: $LAST (rate limit 5/15min — 7 ta tez so'rov)"; fi

echo ""
echo "6. CORS — noma'lum origin"
ORIGIN=$(curl -s -D- -o /dev/null -X OPTIONS "$BASE/api/v1/auth/me" \
  -H "Origin: http://evil.com" -H "Access-Control-Request-Method: GET" 2>&1 | grep -i "access-control-allow-origin: http://evil")
if [ -z "$ORIGIN" ]; then echo "   ✅ evil.com bloklangan"; else echo "   ❌ evil.com ruxsat berilgan"; fi

echo ""
echo "7. CORS — ruxsat berilgan origin"
ORIGIN=$(curl -s -D- -o /dev/null -X OPTIONS "$BASE/api/v1/auth/me" \
  -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" 2>&1 | grep -i "access-control-allow-origin: http://localhost:3000")
if [ -n "$ORIGIN" ]; then echo "   ✅ localhost:3000 ruxsat berilgan"; else echo "   ❌ localhost:3000 bloklangan"; fi

echo ""
echo "════════════════════════════════════════════════════════════"
