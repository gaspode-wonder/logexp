# filename: logexp/app/services/analytics.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# ----------------------------------------------------------------------
# Logger MUST be named "logexp.analytics" to satisfy test expectations.
# It must propagate to root handlers so caplog can capture it.
# ----------------------------------------------------------------------
import logging
from typing import Any, Dict, List, Optional

from flask import current_app
from sqlalchemy.exc import OperationalError

from logexp.app.extensions import db
from logexp.app.models import LogExpReading

logger = logging.getLogger("logexp.analytics")
logger.setLevel(logging.INFO)
logger.propagate = True


def compute_window(now: Optional[datetime] = None) -> List[LogExpReading]:
    current: datetime = now or datetime.now(timezone.utc)

    window_seconds: int = current_app.config_obj["ANALYTICS_WINDOW_SECONDS"]
    cutoff: datetime = current - timedelta(seconds=window_seconds)

    try:
        return (
            db.session.query(LogExpReading)
            .filter(LogExpReading.timestamp >= cutoff)
            .order_by(LogExpReading.timestamp.asc())
            .all()
        )
    except OperationalError as exc:
        if "no such table" in str(exc):
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
        return None

    # --- ALWAYS LOG START ---
    logger.info("analytics_start")

    readings = compute_window()

    if not readings:
        # --- ALWAYS LOG COMPLETE ---
        logger.info("analytics_complete")
        return None

    cps_values = [r.counts_per_second for r in readings]

    result = {
        "count": len(readings),
        "avg_cps": sum(cps_values) / len(cps_values),
        "first_timestamp": readings[0].timestamp,
        "last_timestamp": readings[-1].timestamp,
    }

    # --- ALWAYS LOG COMPLETE ---
    logger.info("analytics_complete")

    return result
