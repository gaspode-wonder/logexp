#!/usr/bin/env bash
# filename: beamfoundry/entrypoint.sh
set -euo pipefail

cd /opt/logexp

export FLASK_APP="beamfoundry:create_app"
export FLASK_ENV="production"

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    flask db upgrade || {
        echo "Migration failed"
        exit 1
    }
fi

exec "$@"
