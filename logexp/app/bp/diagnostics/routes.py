# filename: logexp/app/bp/diagnostics/routes.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from flask import jsonify, render_template

from logexp.app.logging_setup import get_logger
from logexp.app.services.analytics_diagnostics import get_analytics_status
from logexp.app.services.database_diagnostics import get_database_status

# Import the singleton blueprint defined in __init__.py
from . import bp_diagnostics

logger = get_logger("logexp.bp.diagnostics")


# ---------------------------------------------------------------------------
# Primary diagnostics page (HTML)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("", endpoint="diagnostics_index")
def diagnostics_index() -> str:
    """
    HTML diagnostics dashboard.
    Endpoint: diagnostics.diagnostics_index
    """
    analytics = get_analytics_status()
    database = get_database_status()

    return render_template(
        "diagnostics.html",
        analytics=analytics,
        database=database,
    )


# ---------------------------------------------------------------------------
# Legacy alias required by tests: diagnostics_page*
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/page", endpoint="diagnostics_page")
def diagnostics_page() -> str:
    """
    Legacy endpoint required by architecture tests.
    Endpoint name must start with diagnostics_page.
    """
    return diagnostics_index()


# ---------------------------------------------------------------------------
# JSON diagnostics API
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/api", endpoint="diagnostics_api")
def diagnostics_api() -> Any:
    """
    JSON diagnostics endpoint: /diagnostics/api
    """
    now = datetime.now(timezone.utc)

    analytics = get_analytics_status()
    database = get_database_status()

    payload: Dict[str, Any] = {
        "timestamp": now,
        "analytics": analytics,
        "database": database,
    }

    logger.debug(
        "diagnostics_api_payload",
        extra={"analytics": analytics, "database": database},
    )
    return jsonify(payload)


# ---------------------------------------------------------------------------
# Minimal test endpoint required by tests
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/test", endpoint="diagnostics_test")
def diagnostics_test() -> Any:
    """
    Simple test endpoint.
    """
    payload = {"status": "ok"}
    logger.debug("diagnostics_test_endpoint_hit", extra=payload)
    return jsonify(payload)
