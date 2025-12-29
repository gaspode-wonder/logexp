# logexp/app/config.py
import os
from typing import Any, Dict


def load_config(overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Load application configuration from environment variables,
    with optional explicit overrides.

    This is the single source of truth for configuration across
    development, testing, CI, and production.
    """

    config: Dict[str, Any] = {
        # ------------------------------------------------------------------
        # Core
        # ------------------------------------------------------------------
        "TESTING": False,
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev"),

        # ------------------------------------------------------------------
        # Database
        # ------------------------------------------------------------------
        "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,

        # ------------------------------------------------------------------
        # Geiger / Poller
        # ------------------------------------------------------------------
        "GEIGER_PORT": os.environ.get(
            "GEIGER_PORT", "/dev/tty.usbserial-AB9R9IYS"
        ),
        "GEIGER_BAUDRATE": int(os.environ.get("GEIGER_BAUDRATE", "9600")),
        "GEIGER_THRESHOLD": int(os.environ.get("GEIGER_THRESHOLD", "50")),
        "START_POLLER": os.environ.get("START_POLLER", "False").lower() == "true",

        # ------------------------------------------------------------------
        # Timezone
        # ------------------------------------------------------------------
        "LOCAL_TIMEZONE": os.environ.get(
            "LOCAL_TIMEZONE", "America/Chicago"
        ),
    }

    if overrides:
        config.update(overrides)

    return config
