# filename: docker/entrypoint.sh
#!/usr/bin/env bash
set -euo pipefail

echo "[$(date --iso-8601=seconds)] entrypoint: starting container"

# Wait for Postgres if using a Postgres URI
if [[ "${SQLALCHEMY_DATABASE_URI:-}" == postgresql* ]]; then
  echo "[$(date --iso-8601=seconds)] entrypoint: waiting for Postgres..."
  until python - << 'PYCODE'
import os, time
import sqlalchemy as sa

uri = os.environ["SQLALCHEMY_DATABASE_URI"]
engine = sa.create_engine(uri, pool_pre_ping=True)
with engine.connect() as conn:
    conn.execute(sa.text("SELECT 1"))
PYCODE
  do
    echo "[$(date --iso-8601=seconds)] entrypoint: Postgres not ready, retrying..."
    sleep 2
  done
  echo "[$(date --iso-8601=seconds)] entrypoint: Postgres is ready"
fi

echo "[$(date --iso-8601=seconds)] entrypoint: running migrations"
flask db upgrade

echo "[$(date --iso-8601=seconds)] entrypoint: starting app: $*"
exec "$@"
