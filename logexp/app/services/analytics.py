# filename: logexp/app/services/analytics.py
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from flask import current_app
from sqlalchemy import func
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


def compute_window(
    now: Optional[datetime] = None,
    db_session: Any = None,
) -> List[LogExpReading]:
    """
    Return all readings within the configured analytics window.
    NO timestamp normalization is performed.
    """
    session = db_session or db.session

    # ------------------------------------------------------------------
    # Infer `now` from MAX(timestamp) with no normalization.
    # ------------------------------------------------------------------
    if now is None:
        try:
            max_ts = session.query(func.max(LogExpReading.timestamp)).scalar()
        except OperationalError as exc:
            if "no such table" in str(exc):
                logger.debug(
                    "analytics_window_no_table",
                    extra={"error": str(exc)},
                )
                return []
            raise

        if max_ts is None:
            return []

        now = max_ts

    # Type narrowing for Pylance/mypy
    assert now is not None
    current: datetime = now

    # Read window size from app.config (NOT config_obj)
    window_seconds: int = int(current_app.config["ANALYTICS_WINDOW_SECONDS"])
    cutoff: datetime = current - timedelta(seconds=window_seconds)

    logger.debug(
        "analytics_compute_window",
        extra={
            "now": str(current),
            "window_seconds": window_seconds,
            "cutoff": str(cutoff),
        },
    )

    # ------------------------------------------------------------------
    # Fetch all readings >= cutoff, sorted ascending.
    # ------------------------------------------------------------------
    try:
        rows = cast(
            List[LogExpReading],
            (
                session.query(LogExpReading)
                .filter(LogExpReading.timestamp >= cutoff)
                .order_by(LogExpReading.timestamp.asc())
                .all()
            ),
        )

        logger.debug(
            "analytics_window_rows_fetched",
            extra={"count": len(rows)},
        )

        return rows

    except OperationalError as exc:
        if "no such table" in str(exc):
            logger.debug(
                "analytics_window_no_table",
                extra={"error": str(exc)},
            )
            return []
        raise


def run_analytics(
    db_session: Any = None,
    now: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """
    Must emit:
      - analytics_start
      - analytics_complete
    using logger name "logexp.analytics".
    """
    enabled = current_app.config.get("ANALYTICS_ENABLED")
    if enabled is False:
        logger.debug("analytics_disabled")
        return None

    logger.info("analytics_start")

    readings = compute_window(now=now, db_session=db_session)

    if not readings:
        logger.debug("analytics_no_readings")
        logger.info("analytics_complete")
        return None

    cps_values = [r.counts_per_second for r in readings]
    count = len(cps_values)
    avg_cps = sum(cps_values) / count

    result: Dict[str, Any] = {
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
            "first_timestamp": str(readings[0].timestamp),
            "last_timestamp": str(readings[-1].timestamp),
        },
    )

    logger.info("analytics_complete")
    return result
