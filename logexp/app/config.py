# filename: logexp/app/config.py
# Canonical configuration schema and loader for LogExp.
# Provides deterministic layering: defaults → environment → explicit overrides.

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional, Tuple

from logexp.app.logging_setup import get_logger

# Explicit environment variable contract for CI and maintainers
REQUIRED_ENV_VARS: dict[str, str] = {
    "SQLALCHEMY_DATABASE_URI": "Database connection string",
    "LOCAL_TIMEZONE": "Local timezone name",
}

OPTIONAL_ENV_VARS: dict[str, str] = {
    "GEIGER_THRESHOLD": "Float threshold for diagnostics",
    "START_POLLER": "Enable/disable hardware poller",
    "LOGEXP_NODE_ID": "Node identifier for ingestion",
    "TELEMETRY_ENABLED": "Enable telemetry",
    "TELEMETRY_INTERVAL_SECONDS": "Telemetry interval",
}

logger = get_logger("logexp.config")

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
    # Telemetry
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
        raw: Optional[str] = os.environ.get(env_var)
        if raw is not None:
            try:
                config[key] = caster(raw)
                logger.debug(
                    "config_env_applied",
                    extra={"key": key, "env_var": env_var, "value": config[key]},
                )
            except Exception as exc:
                logger.error(
                    "config_env_invalid",
                    extra={"env_var": env_var, "raw": raw, "error": str(exc)},
                )
                raise ValueError(f"Invalid value for {env_var}: {raw!r}")

    # 2. Apply explicit overrides
    if overrides:
        logger.debug(
            "config_overrides_applied",
            extra={"override_keys": list(overrides.keys())},
        )
        config.update(overrides)

    # 3. Normalize GEIGER_THRESHOLD to float
    try:
        config["GEIGER_THRESHOLD"] = float(config["GEIGER_THRESHOLD"])
    except Exception:
        raise ValueError(f"Invalid value for GEIGER_THRESHOLD: {config['GEIGER_THRESHOLD']!r}")

    # 4. Normalize START_POLLER to boolean
    val = config.get("START_POLLER")
    if isinstance(val, str):
        config["START_POLLER"] = val.strip().lower() in ("1", "true", "yes", "on")
    else:
        config["START_POLLER"] = bool(val)

    # 5. Normalize TELEMETRY_ENABLED to boolean
    tval = config.get("TELEMETRY_ENABLED")
    if isinstance(tval, str):
        config["TELEMETRY_ENABLED"] = tval.strip().lower() in ("1", "true", "yes", "on")
    else:
        config["TELEMETRY_ENABLED"] = bool(tval)

    # 6. Normalize TELEMETRY_INTERVAL_SECONDS to int
    try:
        config["TELEMETRY_INTERVAL_SECONDS"] = int(config["TELEMETRY_INTERVAL_SECONDS"])
    except Exception:
        raise ValueError(
            f"Invalid value for TELEMETRY_INTERVAL_SECONDS: "
            f"{config['TELEMETRY_INTERVAL_SECONDS']!r}"
        )

    # 7. Apply engine options based on database backend
    uri = str(config.get("SQLALCHEMY_DATABASE_URI") or "")
    if uri.startswith("sqlite://"):
        import sqlite3

        config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES}
        }
    else:
        config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

    logger.debug(
        "config_load_complete",
        extra={"final_keys": list(config.keys())},
    )

    return config
