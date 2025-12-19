#!/bin/sh
set -e

echo "$(date +"%Y-%m-%d %H:%M:%S") | Starting LogExp entrypoint..."

if [ -z "$SQLALCHEMY_DATABASE_URI" ]; then
  echo "$(date +"%Y-%m-%d %H:%M:%S") | ERROR: SQLALCHEMY_DATABASE_URI is not set"
  exit 1
fi

echo "$(date +"%Y-%m-%d %H:%M:%S") | Running flask db upgrade..."
flask db upgrade

echo "$(date +"%Y-%m-%d %H:%M:%S") | Seeding data (if needed)..."
flask seed-data || echo "Seed command failed or not defined; continuing."

echo "$(date +"%Y-%m-%d %H:%M:%S") | Starting application: $*"
exec "$@"
