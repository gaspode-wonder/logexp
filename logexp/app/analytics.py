# logexp/app/analytics.py

from datetime import datetime, timedelta
from flask import current_app
from logexp.app.models import LogExpReading
from logexp.app.extensions import db


def compute_window():
    """
    Return all readings within the configured analytics window.
    """
    config = current_app.config_obj
    window_seconds = config["ANALYTICS_WINDOW_SECONDS"]

    cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)

    return (
        db.session.query(LogExpReading)
        .filter(LogExpReading.timestamp >= cutoff)
        .order_by(LogExpReading.timestamp.asc())
        .all()
    )


def compute_rollup(readings):
    """
    Placeholder rollup logic — will be expanded in Step 8C/8D.
    """
    if not readings:
        return None

    # Example: simple average CPS
    avg_cps = sum(r.counts_per_second for r in readings) / len(readings)

    return {
        "count": len(readings),
        "avg_cps": avg_cps,
        "first_timestamp": readings[0].timestamp,
        "last_timestamp": readings[-1].timestamp,
    }


def run_analytics():
    """
    Main analytics entrypoint.
    Called manually or by scheduled tasks — never by ingestion.
    """
    config = current_app.config_obj

    if not config["ANALYTICS_ENABLED"]:
        return None

    readings = compute_window()
    return compute_rollup(readings)
