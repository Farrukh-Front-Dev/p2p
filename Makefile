.PHONY: help up down build api bot frontend migrate test lint

help:
	@echo "P2P Platform — buyruqlar:"
	@echo "  make up         — barcha servislarni ishga tushirish (Docker)"
	@echo "  make down       — to'xtatish"
	@echo "  make build      — build qilish"
	@echo "  make api        — backend API (local, .venv)"
	@echo "  make bot        — Telegram bot (local)"
	@echo "  make worker     — Celery worker (local)"
	@echo "  make migrate    — alembic upgrade head"
	@echo "  make test       — backend testlar"
	@echo "  make lint       — ruff check"

# ── Docker ────────────────────────────────────────────────────────────────────
up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

# ── Local dev ────────────────────────────────────────────────────────────────
api:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

bot:
	cd backend && .venv/bin/python -m bot.main

worker:
	cd backend && .venv/bin/celery -A app.tasks.celery_app.celery_app worker --loglevel=info

beat:
	cd backend && .venv/bin/celery -A app.tasks.celery_app.celery_app beat --loglevel=info

frontend:
	cd frontend && npm run dev

# ── DB ────────────────────────────────────────────────────────────────────────
migrate:
	cd backend && .venv/bin/alembic upgrade head

migration:
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(msg)"

# ── QA ────────────────────────────────────────────────────────────────────────
test:
	cd backend && .venv/bin/pytest

lint:
	cd backend && .venv/bin/ruff check .
	cd backend && .venv/bin/python -m py_compile bot/main.py
