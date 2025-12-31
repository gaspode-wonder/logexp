from __future__ import annotations

import datetime

from flask import current_app

from logexp.app.extensions import db
from logexp.app.models import LogExpReading


def compute_window(now=None):
    """
    Deterministic analytics window calculation.

    Tests may pass a fixed 'now' to eliminate microsecond drift.
    Production uses the real current time.
    """
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)

    config = current_app.config_obj
    window_seconds = config["ANALYTICS_WINDOW_SECONDS"]

    cutoff = now - datetime.timedelta(seconds=window_seconds)

    rows = db.session.query(LogExpReading).order_by(LogExpReading.id.asc()).all()

    result = []
    for r in rows:
        ts = r.timestamp_dt
        if ts >= cutoff:
            result.append(r)

    return result


def run_analytics():
    """
    Legacy/compatibility wrapper used by routes and tests.

    Tests expect:
    - None when analytics is disabled
    - None when the window is empty
    - Summary dict otherwise
    """
    config = current_app.config_obj

    if not config.get("ANALYTICS_ENABLED", True):
        return None

    readings = compute_window()

    if not readings:
        return None

    cps_values = [r.counts_per_second for r in readings]
    timestamps = [r.timestamp_dt for r in readings]

    return {
        "count": len(readings),
        "avg_cps": sum(cps_values) / len(cps_values),
        "first_timestamp": min(timestamps),
        "last_timestamp": max(timestamps),
    }
