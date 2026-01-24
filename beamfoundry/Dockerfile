# filename: Dockerfile

FROM python:3.10-slim AS builder

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY beamfoundry/docker-requirements.txt .
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r docker-requirements.txt

COPY pyproject.toml .
COPY app/ app/
COPY beamfoundry/ .
COPY alembic.ini .

FROM python:3.10-slim AS runtime

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m logexp

COPY --from=builder /install /usr/local

COPY pyproject.toml .
COPY app/ app/
COPY beamfoundry/ .
COPY alembic.ini .
COPY beamfoundry/gunicorn.conf.py beamfoundry/gunicorn.conf.py
COPY beamfoundry/entrypoint.sh /entrypoint.sh

USER root
RUN chmod +x /entrypoint.sh

# Install the package as root so egg-info can be created
RUN pip install .

USER logexp

ENV FLASK_APP=beamfoundry:create_app
ENV FLASK_ENV=production

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "beamfoundry/gunicorn.conf.py", "beamfoundry:create_app"]
