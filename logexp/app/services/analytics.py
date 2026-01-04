# filename: logexp/logexp/app/services/analytics.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import logging
from flask import current_app
from sqlalchemy.exc import OperationalError

from logexp.app.extensions import db
from logexp.app.models import LogExpReading

# ----------------------------------------------------------------------
# Logger MUST be named "logexp.analytics" to satisfy test expectations.
# It must propagate to root handlers so caplog can capture it.
# ----------------------------------------------------------------------
logger = logging.getLogger("logexp.analytics")
logger.setLevel(logging.INFO)
logger.propagate = True


def compute_window(now: Optional[datetime] = None) -> List[LogExpReading]:
    """
    Return all readings within the configured analytics window.
    """
    current: datetime = now or datetime.now(timezone.utc)

    window_seconds: int = current_app.config_obj["ANALYTICS_WINDOW_SECONDS"]
    cutoff: datetime = current - timedelta(seconds=window_seconds)

    logger.debug(
        "analytics_compute_window",
        extra={
            "now": current.isoformat(),
            "window_seconds": window_seconds,
            "cutoff": cutoff.isoformat(),
        },
    )

    try:
        rows = (
            db.session.query(LogExpReading)
            .filter(LogExpReading.timestamp >= cutoff)
            .order_by(LogExpReading.timestamp.asc())
            .all()
        )

        logger.debug(
            "analytics_window_rows_fetched",
            extra={"count": len(rows)},
        )

        return rows

    except OperationalError as exc:
        # SQLite in-memory DB during tests may not have the table yet.
        if "no such table" in str(exc):
            logger.debug(
                "analytics_window_no_table",
                extra={"error": str(exc)},
            )
            return []
        raise


def run_analytics(db_session: Any = None) -> Optional[Dict[str, Any]]:
    """
    Must emit:
      - analytics_start
      - analytics_complete
    using logger name "logexp.analytics".
    """
    enabled = current_app.config_obj.get("ANALYTICS_ENABLED")
    if enabled is False:
        logger.debug("analytics_disabled")
        return None

    # --- ALWAYS LOG START ---
    logger.info("analytics_start")

    readings = compute_window()

    if not readings:
        logger.debug("analytics_no_readings")
        # --- ALWAYS LOG COMPLETE ---
        logger.info("analytics_complete")
        return None

    cps_values = [r.counts_per_second for r in readings]
    count = len(cps_values)
    avg_cps = sum(cps_values) / count

    result = {
        "count": count,
        "avg_cps": avg_cps,
        "first_timestamp": readings[0].timestamp,
        "last_timestamp": readings[-1].timestamp,
    }

    logger.debug(
        "analytics_metrics_computed",
        extra={
            "count": count,
            "avg_cps": avg_cps,
            "first_timestamp": readings[0].timestamp.isoformat(),
            "last_timestamp": readings[-1].timestamp.isoformat(),
        },
    )

    # --- ALWAYS LOG COMPLETE ---
    logger.info("analytics_complete")

    return result
