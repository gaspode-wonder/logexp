# filename: Dockerfile
# Canonical, future‑proof, two‑stage build for LogExp

##############################
# 1. BUILDER STAGE
##############################
FROM python:3.10-slim AS builder

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into /install (isolated from system)
COPY docker-requirements.txt .
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r docker-requirements.txt

# Copy only what is needed for dependency resolution
COPY pyproject.toml .
COPY logexp/ logexp/

##############################
# 2. RUNTIME STAGE
##############################
FROM python:3.10-slim AS runtime

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Runtime system deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Bring in all Python deps from builder
COPY --from=builder /install /usr/local

# Copy application code and metadata required for editable install
COPY pyproject.toml .
COPY logexp/ logexp/
COPY migrations/ migrations/
COPY alembic.ini .
COPY gunicorn.conf.py .
COPY wsgi.py .

# Install the package in editable mode (safe because metadata is present)
RUN pip install -e .

ENV FLASK_APP=beamfoundry.app:create_app
ENV FLASK_ENV=production

# Entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
