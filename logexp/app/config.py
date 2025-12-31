# logexp/app/config.py
# Canonical configuration schema and loader for LogExp.
# Provides deterministic layering: defaults → environment → explicit overrides.
# Timestamp: 2025-12-30 22:48 CST

import os
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Base Defaults (single source of truth)
# ---------------------------------------------------------------------------
DEFAULTS: Dict[str, Any] = {
    # Core
    "TESTING": False,
    "SECRET_KEY": "dev",
    # Database
    "SQLALCHEMY_DATABASE_URI": None,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    # Geiger / Poller
    "GEIGER_PORT": "/dev/tty.usbserial-AB9R9IYS",
    "GEIGER_BAUDRATE": 9600,
    "GEIGER_THRESHOLD": 50,
    "START_POLLER": False,
    # Timezone
    "LOCAL_TIMEZONE": "America/Chicago",
    # Analytics
    "ANALYTICS_WINDOW_SECONDS": 60,
    "ANALYTICS_ENABLED": False,  # future-proof for Step 11E
}


# ---------------------------------------------------------------------------
# Environment Variable Mapping
# ---------------------------------------------------------------------------
ENV_MAP = {
    "SECRET_KEY": ("SECRET_KEY", str),
    "SQLALCHEMY_DATABASE_URI": ("DATABASE_URL", str),
    "GEIGER_PORT": ("GEIGER_PORT", str),
    "GEIGER_BAUDRATE": ("GEIGER_BAUDRATE", int),
    "GEIGER_THRESHOLD": ("GEIGER_THRESHOLD", int),
    "START_POLLER": ("START_POLLER", lambda v: v.lower() == "true"),
    "LOCAL_TIMEZONE": ("LOCAL_TIMEZONE", str),
    "ANALYTICS_WINDOW_SECONDS": ("ANALYTICS_WINDOW_SECONDS", int),
    "ANALYTICS_ENABLED": ("ANALYTICS_ENABLED", lambda v: v.lower() == "true"),
}


# ---------------------------------------------------------------------------
# Config Loader
# ---------------------------------------------------------------------------
def load_config(overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Load application configuration with deterministic layering:

        1. DEFAULTS (single source of truth)
        2. Environment variables (typed)
        3. Explicit overrides (tests, CI, dev)

    Returns a plain dictionary used by the application factory.
    """

    config = DEFAULTS.copy()

    # 1. Apply environment variables
    for key, (env_var, caster) in ENV_MAP.items():
        raw = os.environ.get(env_var)
        if raw is not None:
            try:
                config[key] = caster(raw)
            except Exception:
                raise ValueError(f"Invalid value for {env_var}: {raw!r}")

    # 2. Apply explicit overrides
    if overrides:
        config.update(overrides)

    return config
