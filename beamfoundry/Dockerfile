# filename: Dockerfile

FROM python:3.10-slim AS builder

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY docker-requirements.txt .
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r docker-requirements.txt

COPY pyproject.toml .
COPY app/ app/
COPY beamfoundry/ beamfoundry/

FROM python:3.10-slim AS runtime

WORKDIR /opt/logexp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m logexp
USER logexp

COPY --from=builder /install /usr/local

COPY pyproject.toml .
COPY app/ app/
COPY beamfoundry/ beamfoundry/
COPY alembic.ini .
COPY gunicorn.conf.py .
COPY wsgi.py .

RUN pip install .

ENV FLASK_APP=beamfoundry:create_app
ENV FLASK_ENV=production

COPY beamfoundry/entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh
USER logexp

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
