# filename: logexp/validation/config_validator.py

"""
Validation for application configuration values.

Ensures that config values are well-typed, within expected ranges, and safe
for analytics and ingestion.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

from logexp.app.logging_setup import get_logger

log = get_logger("logexp.validation.config_validator")


def validate_config(cfg: dict) -> dict:
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
        raise ValueError("ANALYTICS_WINDOW must be a positive integer")

    # ------------------------------------------------------------
    # LOCAL_TIMEZONE must be valid
    # ------------------------------------------------------------
    tz = cfg["LOCAL_TIMEZONE"]
    try:
        ZoneInfo(tz)
    except Exception:
        raise ValueError(f"Invalid timezone: {tz}")

    # ------------------------------------------------------------
    # INGESTION_ENABLED must be boolean
    # ------------------------------------------------------------
    if not isinstance(cfg["INGESTION_ENABLED"], bool):
        raise ValueError("INGESTION_ENABLED must be a boolean")

    return cfg
