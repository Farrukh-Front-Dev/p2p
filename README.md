# P2P Platform

School21 talabalar uchun peer-to-peer o'qitish platformasi.

## Struktura

```
p2p/
├── backend/          FastAPI REST API + WebSocket + Celery
├── bot/              Telegram bot (python-telegram-bot 21.x)
├── frontend/         React + Vite + TypeScript
├── docker-compose.yml
└── Makefile
```

## Tezkor ishga tushirish

```bash
# Barcha servislar (Docker)
make up

# Faqat local dev
make api       # http://localhost:8000
make bot       # Telegram bot
make frontend  # http://localhost:5173
```

## Muhit o'zgaruvchilari

```bash
cp backend/.env.example backend/.env
# .env ni to'ldiring: FERNET_KEY, JWT_SECRET_KEY, TELEGRAM_BOT_TOKEN, ...
```

## Batafsil

- [backend/README.md](backend/README.md) — API, migratsiya, Celery
- API Swagger: `http://localhost:8000/docs`
- Admin panel: `http://localhost:8000/admin`







teacher va pupil niki ko'rinsin oxirgi 15 minutda bir biriga



nechtadir proverkada auto badge berish kerak 
