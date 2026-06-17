#!/bin/bash
set -e

# ── Start PostgreSQL ─────────────────────────────────────────────────────────
echo "Starting PostgreSQL..."
su - postgres -c "/usr/lib/postgresql/*/bin/pg_ctl -D /var/lib/postgresql/data -l /var/lib/postgresql/logfile start"

# Create database and user if not exists
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='peerlearn'\" | grep -q 1 || psql -c \"CREATE USER peerlearn WITH PASSWORD 'strongpassword';\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='peer_learn'\" | grep -q 1 || psql -c \"CREATE DATABASE peer_learn OWNER peerlearn;\""

# ── Start Redis ──────────────────────────────────────────────────────────────
echo "Starting Redis..."
redis-server --daemonize yes

# ── Run Alembic migrations ───────────────────────────────────────────────────
echo "Running Alembic migrations..."
cd /app
alembic upgrade head || echo "Migration warning — check logs"

# ── Start all services via supervisord ───────────────────────────────────────
echo "Starting API + Bot + Celery..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
