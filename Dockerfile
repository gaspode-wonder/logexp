# filename: Dockerfile

# =============================================================================
# BUILDER STAGE — install build dependencies, compile wheels, isolate artifacts
# =============================================================================
FROM python:3.10-slim AS builder

# System deps required for building psycopg2-binary, numpy, matplotlib, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/logexp

# Install pip + wheel tooling
RUN pip install --upgrade pip setuptools wheel

# Copy project metadata + requirements first for caching
COPY pyproject.toml .
COPY requirements.txt .

# Build wheels for all dependencies
RUN pip wheel --wheel-dir /opt/wheels -r requirements.txt


# =============================================================================
# RUNTIME STAGE — minimal, production-grade Python environment
# =============================================================================
FROM python:3.10-slim AS runtime

# System runtime deps (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/logexp

# Install wheels built in the builder stage
COPY --from=builder /opt/wheels /opt/wheels
RUN pip install --no-cache-dir /opt/wheels/*

# Copy application code
COPY logexp /opt/logexp/logexp

# Copy migrations explicitly
COPY logexp/migrations /opt/logexp/logexp/migrations

# No instance/ directory — removed because you do not use SQLite files in Docker
# (CI uses in-memory SQLite; production uses Postgres)
# COPY instance /opt/logexp/instance   ← intentionally removed

# Gunicorn config (if you add one later)
# COPY gunicorn.conf.py /opt/logexp/gunicorn.conf.py

# Environment defaults (can be overridden at runtime)
ENV FLASK_APP="logexp.app:create_app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose Flask/Gunicorn port
EXPOSE 8000

# Default command: run Gunicorn with your Flask factory
CMD ["gunicorn", "-b", "0.0.0.0:8000", "logexp.app:create_app"]
