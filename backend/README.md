# P2P Platform

School21 peer-to-peer o'qitish tizimi. Talabalar bir-birlarini slotlar orqali
o'qitadi; XP, Level, Peer Points va Peer Coins — to'liq platforma ichki tizim
(School21 API dan mustaqil).

## Stack

- **Backend:** Python 3.11+ · FastAPI · SQLAlchemy 2.0 async · Alembic
- **Real-time:** FastAPI WebSocket (native ASGI) + Redis Pub/Sub
- **Background:** Celery + Celery Beat · Redis broker
- **DB:** PostgreSQL 15 · Redis 7
- **Bot:** python-telegram-bot 21.x
- **Admin:** SQLAdmin

## Loyiha strukturasi

```
peer_learn/
├── app/
│   ├── main.py                 # FastAPI app, lifespan, router mount
│   ├── core/                   # config, security, dependencies
│   ├── db/                     # async engine + models (1 fayl = 1 model)
│   ├── api/v1/                 # REST endpointlar
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # biznes logika (slot, matching, xp, points, ...)
│   ├── tasks/                  # Celery app + scheduled tasks
│   └── ws/                     # WebSocket handler + connection manager
├── admin/setup.py              # SQLAdmin views
├── bot/                        # Telegram bot
├── alembic/                    # migratsiyalar
└── docker/                     # Dockerfile, compose, nginx
```

## Local ishga tushirish

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # qiymatlarni to'ldiring (FERNET_KEY, JWT_SECRET_KEY, ...)

# FERNET_KEY yaratish:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Migratsiya yaratish va qo'llash (postgres ishga tushgan bo'lsin):
alembic revision --autogenerate -m "initial"
alembic upgrade head

# API:
uvicorn app.main:app --reload

# Celery worker / beat (alohida terminallarda):
celery -A app.tasks.celery_app.celery_app worker --loglevel=info
celery -A app.tasks.celery_app.celery_app beat --loglevel=info

# Bot:
python -m bot.main
```

## Docker

```bash
cd docker
docker compose up --build
```

## API

Swagger UI: `http://localhost:8000/docs`. Barcha endpointlar `/api/v1/` ostida.
Admin panel: `http://localhost:8000/admin`.

## Eslatma

School21 API dan FAQAT login/profil/loyihalar/skills/coalition/location olinadi.
XP, Level, Peer Points, Peer Coins hech qachon School21 dan olinmaydi.
