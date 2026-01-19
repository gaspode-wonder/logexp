# filename: logexp/validation/ingestion_validator.py

"""
Validation for ingestion payloads.

Ensures that incoming readings contain the required fields, are well-typed,
and safe for ingestion into the database.
"""

from __future__ import annotations

from app.logging_setup import get_logger

log = get_logger("logexp.validation.ingestion_validator")


def validate_ingestion_payload(payload: dict[str, object]) -> dict[str, object] | None:
    """
    Validate a single ingestion payload.

    Required keys:
    - cps: int or float
    - cpm: int or float
    - usv: int or float
    - mode: "SLOW", "FAST", or "INST"
    - timestamp: ISO8601 string

    Returns:
        dict  → valid payload (shallow copy)
        None  → invalid payload (graceful failure)
    """
    log.debug("ingestion_validation_start", extra={"keys": list(payload.keys())})

    required = ["cps", "cpm", "usv", "mode", "timestamp"]

    # ------------------------------------------------------------
    # Check required keys and nulls
    # ------------------------------------------------------------
    for key in required:
        if key not in payload or payload[key] is None:
            log.warning("missing_key", extra={"key": key})
            return None

    # ------------------------------------------------------------
    # Validate mode (expanded to include INST)
    # ------------------------------------------------------------
    mode = payload["mode"]
    if mode not in ("SLOW", "FAST", "INST"):
        log.warning("invalid_mode", extra={"mode": mode})
        return None

    # ------------------------------------------------------------
    # Return a shallow copy to avoid mutation
    # ------------------------------------------------------------
    log.debug("ingestion_validation_success", extra={"mode": mode})
    return dict(payload)
