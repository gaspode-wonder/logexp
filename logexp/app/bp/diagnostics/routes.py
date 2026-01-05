# filename: logexp/app/bp/analytics/routes.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from flask import jsonify, render_template

from logexp.app.logging_setup import get_logger
from logexp.app.services.analytics_diagnostics import get_analytics_status
from logexp.app.services.database_diagnostics import get_database_status
from logexp.app.services.ingestion import get_ingestion_status

# Import the singleton blueprint defined in __init__.py
from . import bp_analytics

logger = get_logger("logexp.bp.analytics")


@bp_analytics.get("", endpoint="analytics_index")
def analytics_index() -> str:
    """
    HTML analytics dashboard.
    """
    analytics: Dict[str, Any] = get_analytics_status()
    database: Dict[str, Any] = get_database_status()
    ingestion: Dict[str, Any] = get_ingestion_status()

    return render_template(
        "analytics.html",
        analytics=analytics,
        database=database,
        ingestion=ingestion,
    )


@bp_analytics.get("/export", endpoint="analytics_export")
def analytics_export() -> Any:
    """
    JSON analytics export endpoint.
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
        "diagnostics_count": analytics.get("count", 0),
    }

    logger.debug(
        "analytics_export_payload",
        extra={"analytics": analytics, "database": database, "ingestion": ingestion},
    )
    return jsonify(payload)
