#!/usr/bin/env bash
set -euo pipefail

# Ensure the working directory is correct
cd /opt/logexp

# Install the application into the container environment
pip install .

# Export canonical Flask environment variables
export FLASK_APP="beamfoundry:create_app"
export FLASK_ENV="production"

# Run any pending migrations automatically if desired
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    flask db upgrade || {
        echo "Migration failed"
        exit 1
    }
fi

# Execute the container's command (gunicorn by default)
exec "$@"
