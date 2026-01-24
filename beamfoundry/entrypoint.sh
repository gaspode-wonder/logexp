#!/usr/bin/env bash
# filename: entrypoint.sh
set -euo pipefail

cd /opt/logexp

# Export canonical Flask environment variables
export FLASK_APP="beamfoundry:create_app"
export FLASK_ENV="production"

# Run migrations if enabled
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    flask db upgrade || {
        echo "Migration failed"
        exit 1
    }
fi

exec "$@"
