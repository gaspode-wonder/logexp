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

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy app code
COPY . .

# Gunicorn config (already in repo root)
# FLASK_APP used by flask CLI, gunicorn uses wsgi:app
ENV FLASK_APP=logexp.app
ENV FLASK_ENV=production

# Entrypoint (migrations + seeding)
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
