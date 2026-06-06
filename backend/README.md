# PeerLearn Bot — Backend

School 21 talabalari uchun anonim peer-to-peer bilim almashish Telegram boti.

Foydalanuvchilar bilim ulashish uchun **slot ochadi** (mentor) yoki o'rganish uchun **slot band qiladi** (mentee). Bot ikki tarafni anonim birlashtiradi va sessiyadan 15 daqiqa oldin kimligini oshkor qiladi. Coin va XP tizimi orqali adolatli almashinuv ta'minlanadi.

## Texnologiyalar

- Python 3.11+, aiogram 3.x
- FastAPI (webhook), SQLAlchemy 2.x async, Alembic
- PostgreSQL, Redis, APScheduler
- School 21 integratsiyasi: **Keycloak (password grant) + REST API**

## Arxitektura

```
Handlers → Services → Repositories → Models (SQLAlchemy)
              │
              ├── School21Client (Keycloak + REST)
              ├── CoinService / XPService (atomik, idempotent)
              ├── SlotService / SessionService
              ├── ChatService (abstrakt): RelayChatService (MVP) | UserBotChatService (kelajak)
              └── SchedulerService (APScheduler: eslatma + sessiya boshlash)
```

To'liq spec: `.kiro/specs/peerlearn-bot-backend/` (requirements, design, tasks).

## Ishga tushirish (Docker)

```bash
# 1. .env yaratish
cp .env.example .env
# .env ni to'ldiring (BOT_TOKEN, SECRET_KEY, ...)

# 2. Docker bilan ishga tushirish
docker compose up -d --build

# 3. Migratsiya
docker compose exec bot alembic upgrade head

# 4. Loglar
docker compose logs -f bot
```

## Lokal ishga tushirish (development)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# PostgreSQL va Redis ishlab turishi kerak (yoki docker compose up postgres redis)
cp .env.example .env   # DEBUG=True qo'ying (polling rejimi)
alembic upgrade head
python -m bot.main
```

`DEBUG=True` → polling rejimi (development).
`DEBUG=False` → webhook rejimi (FastAPI, `:8080`).

## Testlar

```bash
pytest                 # barcha testlar
pytest -m "not slow"   # tez testlar
```

Testlarda PostgreSQL o'rniga SQLite (in-memory), Redis o'rniga fakeredis, School 21 API esa respx orqali mock qilinadi — tashqi xizmatlar shart emas.

## Kod sifati (linting & formatting)

Loyiha `ruff` (linter + formatter) bilan boshqariladi (`ruff.toml`).

```bash
ruff check bot tests          # lint
ruff check bot tests --fix    # avtomatik tuzatish
ruff format bot tests         # formatlash
```

## REST API (Telegram Mini App)

Mini App frontend uchun REST API mavjud (`bot/api/`):

```bash
python -m bot.api_server   # lokal API server (:8080), Swagger: /docs
```

Production'da `webhook_server.py` API + Telegram webhook'ni birga yuritadi.

Asosiy endpointlar:
- `POST /api/auth/telegram` — initData orqali kirish (JWT)
- `POST /api/auth/register` — ro'yxatdan o'tishni yakunlash
- `GET /api/me`, `PATCH /api/me` — profil
- `GET /api/slots`, `POST /api/slots`, `POST /api/slots/{id}/book`, `DELETE /api/slots/{id}`
- `GET /api/sessions/active`, `POST /api/sessions/{id}/finish`
- `GET /api/leaderboard`, `GET /api/directions`

## Coin va XP

- Standart: 5 tanga, maksimal 15.
- Slot band qilish: −1 tanga (darhol). O'rgatish: +1 tanga (sessiya tugagach).
- O'rgatish: +50 XP, o'rganish: +25 XP. 7 darajali level tizimi.

## Xavfsizlik eslatmasi

- Webhook endpoint `X-Telegram-Bot-Api-Secret-Token` orqali himoyalangan.
- School 21 paroli hech qayerda saqlanmaydi — faqat ro'yxatdan o'tishda token olish uchun ishlatiladi va xabar darhol o'chiriladi.
- Throttling middleware anti-spam uchun.
