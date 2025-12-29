# logexp/app/config.py
"""
Configuration loader for LogExp.

This module defines load_config(), which constructs the final runtime
configuration by layering:

    1. DEFAULTS (single source of truth)
    2. Environment variable overrides
    3. Explicit overrides (tests, CLI, app factory)

This ensures deterministic, production‑aligned behavior with no config drift.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from logexp.app.config.defaults import DEFAULTS


def _env_bool(value: str | None, default: bool) -> bool:
    """
    Convert an environment variable to a boolean.
    Accepts: "true", "1", "yes" → True
             "false", "0", "no" → False
    Falls back to the provided default.
    """
    if value is None:
        return default

    return value.lower() in ("1", "true", "yes")


def load_config(overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Build the final configuration dictionary.

    Layering order:
        DEFAULTS
        → environment variable overrides
        → explicit overrides (tests, CLI, app factory)

    This function is the only place where environment variables are read.
    """

    # ------------------------------------------------------------------
    # 1. Start with defaults
    # ------------------------------------------------------------------
    config = DEFAULTS.copy()

    # ------------------------------------------------------------------
    # 2. Apply environment variable overrides
    # ------------------------------------------------------------------
    env_overrides = {
        # Core
        "TESTING": _env_bool(os.environ.get("TESTING"), config["TESTING"]),
        "SECRET_KEY": os.environ.get("SECRET_KEY", config["SECRET_KEY"]),

        # Database
        "SQLALCHEMY_DATABASE_URI": os.environ.get(
            "DATABASE_URL", config["SQLALCHEMY_DATABASE_URI"]
        ),

        # Geiger / Poller
        "GEIGER_PORT": os.environ.get("GEIGER_PORT", config["GEIGER_PORT"]),
        "GEIGER_BAUDRATE": int(os.environ.get("GEIGER_BAUDRATE", config["GEIGER_BAUDRATE"])),
        "GEIGER_THRESHOLD": int(os.environ.get("GEIGER_THRESHOLD", config["GEIGER_THRESHOLD"])),
        "START_POLLER": _env_bool(os.environ.get("START_POLLER"), config["START_POLLER"]),

        # Timezone
        "LOCAL_TIMEZONE": os.environ.get("LOCAL_TIMEZONE", config["LOCAL_TIMEZONE"]),

        # Analytics
        "ANALYTICS_ENABLED": _env_bool(
            os.environ.get("ANALYTICS_ENABLED"),
            config["ANALYTICS_ENABLED"],
        ),
        "ANALYTICS_WINDOW_SECONDS": int(
            os.environ.get(
                "ANALYTICS_WINDOW_SECONDS",
                config["ANALYTICS_WINDOW_SECONDS"],
            )
        ),
    }

    config.update(env_overrides)

    # ------------------------------------------------------------------
    # 3. Apply explicit overrides (tests, CLI, app factory)
    # ------------------------------------------------------------------
    if overrides:
        config.update(overrides)

    return config
