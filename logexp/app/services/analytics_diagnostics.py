# filename: logexp/app/services/analytics_diagnostics.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any, Dict, List, Optional, cast

from flask import current_app

from logexp.app.extensions import db
from logexp.app.logging_setup import get_logger
from logexp.app.models import LogExpReading
from logexp.app.typing import LogExpFlask

logger = get_logger("logexp.analytics_diagnostics")


def get_config() -> Dict[str, Any]:
    """
    Typed accessor for application configuration.
    Ensures mypy sees config_obj on the typed Flask subclass.
    """
    return cast(LogExpFlask, current_app).config_obj


def _load_windowed_readings(window_start: datetime) -> List[LogExpReading]:
    """
    Load readings from window_start to now.
    Deterministic ordering (newest first).
    """
    query = (
        db.session.query(LogExpReading)
        .filter(LogExpReading.timestamp >= window_start)
        .order_by(LogExpReading.timestamp.desc())
    )
    readings: List[LogExpReading] = query.all()

    logger.debug(
        "analytics_load_window",
        extra={
            "window_start": window_start.isoformat(),
            "count": len(readings),
        },
    )
    return readings


def summarize_readings(readings: List[LogExpReading]) -> Optional[Dict[str, Any]]:
    """
    Canonical analytics rollup used by diagnostics, routes, and tests.

    Contract:
      - Empty list → None
      - Deterministic under fixed time
      - JSON‑safe values
      - Computes average CPS, CPM, uSv/h
      - Returns the most recent reading timestamp (UTC)
      - Includes 'count' for test expectations
    """
    if not readings:
        logger.debug("analytics_summarize_empty")
        return None

    readings_sorted = sorted(readings, key=lambda r: r.timestamp, reverse=True)

    cps_values = [r.counts_per_second for r in readings_sorted]
    cpm_values = [r.counts_per_minute for r in readings_sorted]
    usv_values = [r.microsieverts_per_hour for r in readings_sorted]

    latest_ts = readings_sorted[0].timestamp.astimezone(timezone.utc)

    summary: Dict[str, Any] = {
        "latest_timestamp": latest_ts,
        "avg_cps": mean(cps_values),
        "avg_cpm": mean(cpm_values),
        "avg_usv": mean(usv_values),
        "count": len(readings_sorted),
    }

    logger.debug("analytics_summarize_complete", extra=summary)
    return summary


def run_analytics_diagnostics() -> Dict[str, Any]:
    """
    Diagnostics payload for the analytics subsystem.

    Contract (aligned with tests):
      - 'window_minutes'
      - 'window_start'
      - 'window_end'
      - 'count'
    """
    config = get_config()

    enabled = config.get("ANALYTICS_ENABLED", True)
    window_minutes = config.get("ANALYTICS_WINDOW_MINUTES", 5)

    window_end = datetime.now(timezone.utc)
    window_start = window_end - timedelta(minutes=window_minutes)

    readings = _load_windowed_readings(window_start)
    summary = summarize_readings(readings)

    result: Dict[str, Any] = {
        "enabled": enabled,
        "window_minutes": window_minutes,
        "window_start": window_start,
        "window_end": window_end,
        "count": summary["count"] if summary is not None else 0,
        "avg_cps": summary["avg_cps"] if summary is not None else None,
        "avg_cpm": summary["avg_cpm"] if summary is not None else None,
        "avg_usv": summary["avg_usv"] if summary is not None else None,
        "latest_timestamp": summary["latest_timestamp"] if summary is not None else None,
    }

    logger.debug("analytics_diagnostics_complete", extra=result)
    return result


def get_analytics_status() -> Dict[str, Any]:
    """
    Backwards‑compatible API expected by diagnostics blueprint and tests.
    No arguments; loads its own windowed readings.
    """
    return run_analytics_diagnostics()
