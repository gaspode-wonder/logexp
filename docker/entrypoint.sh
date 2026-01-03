#!/bin/sh
set -e
set -o pipefail

timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

echo "$(timestamp) | entrypoint_debug_start"

# ---------------------------------------------------------------------------
# Environment + runtime diagnostics
# ---------------------------------------------------------------------------

echo "$(timestamp) | diag_uid_gid | uid=$(id -u) gid=$(id -g)"
echo "$(timestamp) | diag_pwd | pwd=$(pwd)"
echo "$(timestamp) | diag_python | python=$(python3 --version 2>/dev/null || true)"

echo "$(timestamp) | diag_env_begin"
env | sort
echo "$(timestamp) | diag_env_end"

echo "$(timestamp) | diag_filtered_env_begin"
env | sort | grep -E "SQL|FLASK|PYTHON|TZ|ANALYTICS" || true
echo "$(timestamp) | diag_filtered_env_end"

echo "$(timestamp) | diag_pip_freeze_begin"
pip freeze 2>/dev/null || echo "$(timestamp) | diag_pip_freeze_unavailable"
echo "$(timestamp) | diag_pip_freeze_end"

# ---------------------------------------------------------------------------
# Validate required environment variables
# ---------------------------------------------------------------------------

if [ -z "$DATABASE_URL" ]; then
  echo "$(timestamp) | error_missing_env | key=DATABASE_URL"
  exit 1
fi

echo "$(timestamp) | env_ok | key=DATABASE_URL"

# ---------------------------------------------------------------------------
# Run database migrations
# ---------------------------------------------------------------------------

echo "$(timestamp) | migration_start"
flask db upgrade
echo "$(timestamp) | migration_complete"

# ---------------------------------------------------------------------------
# Seed data (idempotent)
# ---------------------------------------------------------------------------

echo "$(timestamp) | seed_start"
if ! flask seed-data; then
  echo "$(timestamp) | seed_nonfatal_failure"
fi
echo "$(timestamp) | seed_complete"

# ---------------------------------------------------------------------------
# Start application
# ---------------------------------------------------------------------------

echo "$(timestamp) | exec_start | cmd=$*"
exec "$@"
