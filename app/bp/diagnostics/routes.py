from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, cast

from flask import Response, jsonify, render_template
from flask_login import login_required

from ...logging_setup import get_logger
from ...services.analytics_diagnostics import get_analytics_status
from ...services.database_diagnostics import get_database_status
from ...services.ingestion import get_ingestion_status
from . import bp_diagnostics

logger = get_logger("beamfoundry.bp.diagnostics")


@bp_diagnostics.get("", endpoint="diagnostics_index")
@login_required
def diagnostics_index() -> Response:
    analytics: Dict[str, Any] = get_analytics_status()
    database: Dict[str, Any] = get_database_status()
    ingestion: Dict[str, Any] = get_ingestion_status()

    html = render_template(
        "diagnostics.html",
        analytics=analytics,
        database=database,
        ingestion=ingestion,
    )
    return Response(html, mimetype="text/html")


@bp_diagnostics.get("/page", endpoint="diagnostics_page")
def diagnostics_page() -> Response:
    return cast(Response, diagnostics_index())


@bp_diagnostics.get("/api", endpoint="diagnostics_api")
def diagnostics_api() -> Response:
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
def diagnostics_test() -> Response:
    payload = {"status": "ok"}
    logger.debug("diagnostics_test_endpoint_hit", extra=payload)
    return jsonify(payload)
