# filename: logexp/app/bp/diagnostics/routes.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from flask import current_app, jsonify, render_template, request

from logexp.app.logging_setup import get_logger
from logexp.app.bp.diagnostics import bp_diagnostics
from logexp.app.services.analytics_diagnostics import get_analytics_status
from logexp.app.services.database_diagnostics import get_database_status
from logexp.app.services.ingestion import get_ingestion_status
from logexp.app.services.poller import get_poller_status

logger = get_logger("logexp.diagnostics")


# ---------------------------------------------------------------------------
# Diagnostics UI (HTML)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/")
def diagnostics_page() -> Any:
    logger.debug(
        "diagnostics_page_requested",
        extra={"path": request.path, "method": request.method},
    )

    config = getattr(current_app, "config_obj", {})
    now = datetime.now(timezone.utc)

    context = {
        "config": dict(config),
        "ingestion": get_ingestion_status(),
        "poller": get_poller_status(),
        "analytics": get_analytics_status(),
        "database": get_database_status(),
        "meta": {
            "timestamp": now.isoformat(),
        },
    }

    logger.debug(
        "diagnostics_page_context_built",
        extra={
            "has_ingestion": context["ingestion"] is not None,
            "has_poller": context["poller"] is not None,
            "has_analytics": context["analytics"] is not None,
            "has_database": context["database"] is not None,
        },
    )

    return render_template("diagnostics.html", **context)


# ---------------------------------------------------------------------------
# Legacy endpoint name used in templates/tests
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/index", endpoint="diagnostics_index")
def diagnostics_index() -> Any:
    logger.debug(
        "diagnostics_index_requested",
        extra={"path": request.path, "method": request.method},
    )
    return diagnostics_page()


# ---------------------------------------------------------------------------
# Support /diagnostics (no trailing slash)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("")
def diagnostics_page_no_slash() -> Any:
    logger.debug(
        "diagnostics_page_no_slash_requested",
        extra={"path": request.path, "method": request.method},
    )
    return diagnostics_page()


# ---------------------------------------------------------------------------
# Minimal JSON test endpoint (legacy)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/geiger/test")
def diagnostics_test() -> Any:
    """
    Legacy JSON test endpoint.
    Retained for backward compatibility with older test suites.
    """
    logger.debug(
        "diagnostics_test_requested",
        extra={"path": request.path, "method": request.method},
    )
    return jsonify({"status": "ok"})
