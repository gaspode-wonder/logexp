# filename: logexp/app/config.py
# Canonical configuration schema and loader for LogExp.
# Provides deterministic layering: defaults → environment → explicit overrides.

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional, Tuple

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.config")

# ---------------------------------------------------------------------------
# Base Defaults (single source of truth)
# ---------------------------------------------------------------------------

DEFAULTS: Dict[str, Any] = {
    "TESTING": False,
    "SECRET_KEY": "dev",
    # Database — resolved in load_config()
    "SQLALCHEMY_DATABASE_URI": None,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    # Geiger / Poller
    "GEIGER_PORT": "/dev/tty.usbserial-AB9R9IYS",
    "GEIGER_BAUDRATE": 9600,
    "GEIGER_THRESHOLD": 50.0,
    "START_POLLER": False,
    # Timezone
    "LOCAL_TIMEZONE": "America/Chicago",
    # Analytics
    "ANALYTICS_WINDOW_SECONDS": 60,
    "ANALYTICS_ENABLED": True,
    # Telemetry
    "LOGEXP_NODE_ID": None,
    "TELEMETRY_ENABLED": False,
    "TELEMETRY_INTERVAL_SECONDS": 60,
}

# ---------------------------------------------------------------------------
# Environment Variable Mapping
# ---------------------------------------------------------------------------

ENV_MAP: Dict[str, Tuple[str, Callable[[str], Any]]] = {
    "SECRET_KEY": ("SECRET_KEY", str),
    "SQLALCHEMY_DATABASE_URI": ("SQLALCHEMY_DATABASE_URI", str),
    "GEIGER_PORT": ("GEIGER_PORT", str),
    "GEIGER_BAUDRATE": ("GEIGER_BAUDRATE", int),
    "GEIGER_THRESHOLD": ("GEIGER_THRESHOLD", float),
    "START_POLLER": ("START_POLLER", lambda v: v.lower() == "true"),
    "LOCAL_TIMEZONE": ("LOCAL_TIMEZONE", str),
    "ANALYTICS_WINDOW_SECONDS": ("ANALYTICS_WINDOW_SECONDS", int),
    "ANALYTICS_ENABLED": ("ANALYTICS_ENABLED", lambda v: v.lower() == "true"),
    "LOGEXP_NODE_ID": ("LOGEXP_NODE_ID", str),
    "TELEMETRY_ENABLED": ("TELEMETRY_ENABLED", lambda v: v.lower() == "true"),
    "TELEMETRY_INTERVAL_SECONDS": ("TELEMETRY_INTERVAL_SECONDS", int),
}

# ---------------------------------------------------------------------------
# Config Loader
# ---------------------------------------------------------------------------


def load_config(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    logger.debug("config_load_start")

    config: Dict[str, Any] = DEFAULTS.copy()

    # 1. Apply environment variables
    for key, (env_var, caster) in ENV_MAP.items():
        raw = os.environ.get(env_var)
        if raw is not None:
            try:
                config[key] = caster(raw)
                logger.debug("config_env_applied", extra={"key": key, "value": config[key]})
            except Exception as exc:
                logger.error("config_env_invalid", extra={"env_var": env_var, "raw": raw})
                raise ValueError(f"Invalid value for {env_var}: {raw!r}") from exc

    # 2. Apply explicit overrides (treat overrides like env vars)
    if overrides:
        for key, value in overrides.items():
            # Allow boolean override for START_POLLER
            if key == "START_POLLER" and isinstance(value, bool):
                config[key] = value
                continue

            # Allow boolean overrides for boolean env vars
            if key in ("ANALYTICS_ENABLED", "TELEMETRY_ENABLED") and isinstance(value, bool):
                config[key] = value
                continue

            if key in ENV_MAP:
                _, caster = ENV_MAP[key]
                try:
                    config[key] = caster(value)
                except Exception as exc:
                    logger.error("config_override_invalid", extra={"key": key, "value": value})
                    raise ValueError(f"Invalid override for {key}: {value!r}") from exc
            else:
                config[key] = value

        logger.debug("config_overrides_applied", extra={"override_keys": list(overrides.keys())})

    # ----------------------------------------------------------------------
    # 3. Resolve SQLALCHEMY_DATABASE_URI deterministically
    # ----------------------------------------------------------------------
    uri = config.get("SQLALCHEMY_DATABASE_URI")

    if uri:
        resolved = uri

    else:
        instance_path = os.path.join(os.getcwd(), "instance")
        os.makedirs(instance_path, exist_ok=True)

        if config.get("TESTING"):
            db_path = os.path.join(instance_path, "test.db")
        elif os.environ.get("CI", "").lower() == "true":
            db_path = os.path.join(instance_path, "ci.db")
        elif os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError("Production requires SQLALCHEMY_DATABASE_URI to be set")
        else:
            db_path = os.path.join(instance_path, "dev.db")

        resolved = f"sqlite:///{db_path}"

    config["SQLALCHEMY_DATABASE_URI"] = resolved
    logger.debug("database_uri_resolved", extra={"uri": resolved})

    # ----------------------------------------------------------------------
    # 4. Engine options (SQLite detect_types)
    # ----------------------------------------------------------------------
    if resolved.startswith("sqlite://"):
        import sqlite3

        config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES}
        }
    else:
        config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

    logger.debug("config_load_complete")
    return config


# Backward‑compatible env var documentation contract for tests

REQUIRED_ENV_VARS = {
    "SQLALCHEMY_DATABASE_URI": "Database connection string (required in production)",
}

OPTIONAL_ENV_VARS = {
    key: f"Environment variable for {key}" for key in ENV_MAP.keys() if key not in REQUIRED_ENV_VARS
}
