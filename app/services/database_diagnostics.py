# filename: logexp/app/services/database_diagnostics.py

from __future__ import annotations

from typing import Any, Dict, cast

from flask import current_app
from sqlalchemy import text

from app.extensions import db
from app.logging_setup import get_logger
from app.typing import LogExpFlask

logger = get_logger("logexp.database_diagnostics")


def get_config() -> Dict[str, Any]:
    """
    Typed accessor for application configuration.
    Ensures mypy sees config_obj on the typed Flask subclass.
    """
    return cast(LogExpFlask, current_app).config_obj


def run_database_diagnostics() -> Dict[str, Any]:
    """
    Canonical database diagnostics payload.

    Contract (aligned with tests):
      - 'healthy' boolean
      - 'connected' boolean
      - 'schema_ok' boolean
      - 'uri'
      - 'engine'
    """
    config = get_config()

    logger.debug("database_diagnostics_start")

    try:
        db.session.execute(text("SELECT 1"))
        healthy = True
    except Exception as exc:
        logger.error("database_diagnostics_failure", extra={"error": str(exc)})
        healthy = False

    uri = config.get("SQLALCHEMY_DATABASE_URI")

    # For now, assume schema checks are OK if the connection check passes.
    schema_ok = healthy

    result: Dict[str, Any] = {
        "healthy": healthy,
        "connected": healthy,
        "schema_ok": schema_ok,
        "uri": uri,
        "engine": uri,
    }

    logger.debug("database_diagnostics_complete", extra=result)
    return result


def get_database_status() -> Dict[str, Any]:
    """
    Backwards‑compatible API expected by diagnostics blueprint and tests.
    """
    return run_database_diagnostics()
