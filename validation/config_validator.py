# filename: logexp/validation/config_validator.py

"""
Validation for application configuration values.

Ensures that config values are well-typed, within expected ranges, and safe
for analytics and ingestion.
"""

from __future__ import annotations

from typing import cast
from zoneinfo import ZoneInfo

from app.logging_setup import get_logger

log = get_logger("logexp.validation.config_validator")


def validate_config(cfg: dict[str, object]) -> dict[str, object]:
    """
    Validate the minimal configuration contract required by tests.

    Required keys:
    - ANALYTICS_WINDOW: int > 0
    - LOCAL_TIMEZONE: valid IANA timezone string
    - INGESTION_ENABLED: bool

    Returns:
        cfg unchanged if valid

    Raises:
        ValueError for invalid window or timezone
    """
    log.debug("config_validation_start", extra={"keys": list(cfg.keys())})

    # ------------------------------------------------------------
    # Required keys
    # ------------------------------------------------------------
    required = ["ANALYTICS_WINDOW", "LOCAL_TIMEZONE", "INGESTION_ENABLED"]
    for key in required:
        if key not in cfg:
            log.error("missing_config_key", extra={"key": key})
            raise ValueError(f"Missing required config key: {key}")

    # ------------------------------------------------------------
    # ANALYTICS_WINDOW must be > 0
    # ------------------------------------------------------------
    window = cfg["ANALYTICS_WINDOW"]
    if not isinstance(window, int) or window <= 0:
        log.error(
            "invalid_analytics_window",
            extra={"value": window},
        )
        raise ValueError("ANALYTICS_WINDOW must be a positive integer")

    # ------------------------------------------------------------
    # LOCAL_TIMEZONE must be valid
    # ------------------------------------------------------------
    tz = cfg["LOCAL_TIMEZONE"]
    try:
        ZoneInfo(cast(str, tz))
    except Exception as exc:
        log.error(
            "invalid_timezone",
            extra={"value": tz, "error": str(exc)},
        )
        raise ValueError(f"Invalid timezone: {tz}")

    # ------------------------------------------------------------
    # INGESTION_ENABLED must be boolean
    # ------------------------------------------------------------
    ingestion_enabled = cfg["INGESTION_ENABLED"]
    if not isinstance(ingestion_enabled, bool):
        log.error(
            "invalid_ingestion_enabled",
            extra={"value": ingestion_enabled},
        )
        raise ValueError("INGESTION_ENABLED must be a boolean")

    log.debug("config_validation_success")
    return cfg
