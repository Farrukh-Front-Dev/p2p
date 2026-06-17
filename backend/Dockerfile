FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies (postgres + redis + supervisor)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev supervisor \
    postgresql postgresql-client redis-server \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Init PostgreSQL data directory
RUN mkdir -p /var/run/postgresql && chown postgres:postgres /var/run/postgresql \
    && su - postgres -c "/usr/lib/postgresql/*/bin/initdb -D /var/lib/postgresql/data"

EXPOSE 8000

CMD ["/start.sh"]
