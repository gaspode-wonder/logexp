# filename: Dockerfile
# Canonical multi‑stage build for LogExp.
# Ensures deterministic dependency installation, explicit migration inclusion,
# and production‑grade runtime environment.

# =========================
# Build stage
# =========================
FROM python:3.10-slim AS builder

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first for caching
COPY docker-requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r docker-requirements.txt

# =========================
# Runtime stage
# =========================
FROM python:3.10-slim AS runtime

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY logexp /opt/logexp/logexp
COPY docker /opt/logexp/docker
COPY gunicorn.conf.py /opt/logexp/gunicorn.conf.py
COPY wsgi.py /opt/logexp/wsgi.py
COPY alembic.ini /opt/logexp/alembic.ini

# Explicitly copy migrations (critical for schema sync)
COPY logexp/migrations /opt/logexp/logexp/migrations

# Explicitly copy instance directory (SQLite dev/test/CI)
COPY instance /opt/logexp/instance

# Gunicorn + Flask config
ENV FLASK_APP=logexp.app
ENV FLASK_ENV=production

# Entrypoint (handles migrations + seeding)
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
