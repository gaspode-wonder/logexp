# filename: Dockerfile

##############################
# Stage 1 — Builder
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

# Install build-time Python deps
COPY beamfoundry/docker-requirements.txt .
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r docker-requirements.txt

# Copy full source once
COPY pyproject.toml .
COPY app/ app/
COPY beamfoundry/ beamfoundry/
COPY alembic.ini .

# 🔥 Ensure no egg-info survives into runtime
RUN rm -rf beamfoundry.egg-info


##############################
# Stage 2 — Runtime
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

# Create non-root user
RUN useradd -m logexp

# Bring in prebuilt wheels and deps
COPY --from=builder /install /usr/local

# Copy full source once
COPY pyproject.toml .
COPY app/ app/
COPY beamfoundry/ beamfoundry/
COPY alembic.ini .

# Runtime-only files
COPY beamfoundry/gunicorn.conf.py beamfoundry/gunicorn.conf.py
COPY beamfoundry/entrypoint.sh /entrypoint.sh

# Fix permissions
RUN chmod +x /entrypoint.sh

# 🔥 Install the package cleanly (no egg-info conflicts)
RUN rm -rf beamfoundry.egg-info && pip install .

USER logexp

ENV FLASK_APP=beamfoundry:create_app
ENV FLASK_ENV=production

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "beamfoundry/gunicorn.conf.py", "beamfoundry:create_app"]
