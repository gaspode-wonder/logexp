#!/bin/sh
set -e

timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

echo "$(timestamp) | Starting LogExp entrypoint..."

# ---------------------------------------------------------------------------
# Validate required environment variables
# ---------------------------------------------------------------------------

if [ -z "$DATABASE_URL" ]; then
  echo "$(timestamp) | ERROR: DATABASE_URL is not set"
  exit 1
fi

echo "$(timestamp) | DATABASE_URL detected"

# ---------------------------------------------------------------------------
# Run database migrations
# ---------------------------------------------------------------------------

echo "$(timestamp) | Running flask db upgrade..."
flask db upgrade

# ---------------------------------------------------------------------------
# Seed data (idempotent)
# ---------------------------------------------------------------------------

echo "$(timestamp) | Seeding data (if needed)..."
if ! flask seed-data; then
  echo "$(timestamp) | Seed command failed or not defined; continuing."
fi

# ---------------------------------------------------------------------------
# Start application
# ---------------------------------------------------------------------------

echo "$(timestamp) | Starting application: $*"
exec "$@"
