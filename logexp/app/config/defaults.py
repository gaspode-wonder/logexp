# logexp/app/config/defaults.py
"""
DEFAULTS: the single source of truth for all configuration values.

Every environment (dev, prod, CI, tests) begins with these defaults.
Environment variables and explicit overrides are layered on top by
load_config() in config.py.

This file must remain side‑effect‑free and import‑safe.
"""

DEFAULTS = {
    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------
    "TESTING": False,
    "SECRET_KEY": "dev",

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    # NOTE: Tests override this to an in‑memory SQLite DB.
    "SQLALCHEMY_DATABASE_URI": "sqlite:///logexp.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    # ------------------------------------------------------------------
    # Geiger / Poller
    # ------------------------------------------------------------------
    "GEIGER_PORT": "/dev/tty.usbserial-AB9R9IYS",
    "GEIGER_BAUDRATE": 9600,
    "GEIGER_THRESHOLD": 50,
    "START_POLLER": False,

    # ------------------------------------------------------------------
    # Polling interval (seconds)
    # ------------------------------------------------------------------
    "POLL_INTERVAL": 1.0,

    # ------------------------------------------------------------------
    # Timezone
    # ------------------------------------------------------------------
    "LOCAL_TIMEZONE": "America/Chicago",

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------
    "ANALYTICS_ENABLED": True,
    "ANALYTICS_WINDOW_SECONDS": 60,

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------
    "INGESTION_ENABLED": True,
    "INGESTION_BATCH_SIZE": 1,
    "INGESTION_RETRY_LIMIT": 3,
    "INGESTION_RETRY_BACKOFF_SECONDS": 1,

}
