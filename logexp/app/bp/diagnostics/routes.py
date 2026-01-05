# filename: logexp/app/bp/diagnostics/routes.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from flask import jsonify, render_template

from logexp.app.logging_setup import get_logger
from logexp.app.services.analytics_diagnostics import get_analytics_status
from logexp.app.services.database_diagnostics import get_database_status
from logexp.app.services.ingestion import get_ingestion_status

# Import the singleton blueprint defined in __init__.py
from . import bp_diagnostics

logger = get_logger("logexp.bp.diagnostics")


@bp_diagnostics.get("", endpoint="diagnostics_index")
def diagnostics_index() -> str:
    """
    HTML diagnostics dashboard.
    """
    analytics: Dict[str, Any] = get_analytics_status()
    database: Dict[str, Any] = get_database_status()
    ingestion: Dict[str, Any] = get_ingestion_status()

    return render_template(
        "diagnostics.html",
        analytics=analytics,
        database=database,
        ingestion=ingestion,
    )


@bp_diagnostics.get("/page", endpoint="diagnostics_page")
def diagnostics_page() -> str:
    """
    Legacy endpoint required by architecture tests.
    """
    return diagnostics_index()


@bp_diagnostics.get("/api", endpoint="diagnostics_api")
def diagnostics_api() -> Any:
    """
    JSON diagnostics endpoint.
    """
    now = datetime.now(timezone.utc)

    analytics: Dict[str, Any] = get_analytics_status()
    database: Dict[str, Any] = get_database_status()
    ingestion: Dict[str, Any] = get_ingestion_status()

    payload: Dict[str, Any] = {
        "timestamp": now,
        "analytics": analytics,
        "database": database,
        "ingestion": ingestion,
    }

    logger.debug(
        "diagnostics_api_payload",
        extra={"analytics": analytics, "database": database, "ingestion": ingestion},
    )
    return jsonify(payload)


@bp_diagnostics.get("/test", endpoint="diagnostics_test")
def diagnostics_test() -> Any:
    """
    Simple test endpoint.
    """
    payload = {"status": "ok"}
    logger.debug("diagnostics_test_endpoint_hit", extra=payload)
    return jsonify(payload)
