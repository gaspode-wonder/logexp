# filename: beamfoundry/Dockerfile

##############################
# Stage 1 — Builder
##############################
FROM python:3.10-slim AS builder

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Build-time system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install build-time Python deps
COPY docker-requirements.txt .
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r docker-requirements.txt

# Copy full source
COPY . .

# Remove any egg-info from repo
RUN rm -rf beamfoundry.egg-info

# Install the package into /install
RUN pip install --prefix=/install .


##############################
# Stage 2 — Runtime
##############################
FROM python:3.10-slim AS runtime

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m logexp

# Bring in installed Python packages
COPY --from=builder /install /usr/local

# Copy source code
COPY . .

# Remove egg-info again to avoid timestamp issues
RUN rm -rf beamfoundry.egg-info

# Fix permissions
RUN chmod +x entrypoint.sh

USER logexp

ENV FLASK_APP=beamfoundry:create_app
ENV FLASK_ENV=production

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "beamfoundry:create_app"]
