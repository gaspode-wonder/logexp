# filename: logexp/app/services/analytics_diagnostics.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from logexp.app.logging_setup import get_logger
from logexp.analytics.diagnostics import (
    get_analytics_status as pure_analytics_status,
)
from logexp.analytics.engine import AnalyticsEngine, ReadingSample
from logexp.app.models import LogExpReading

logger = get_logger("logexp.analytics")


def _get_window_params(
    now: Optional[datetime] = None,
) -> Tuple[int, datetime, datetime]:
    """
    Derive window parameters from config and the current time.

    Returns:
        (window_minutes, window_start, window_end)
    """
    if now is None:
        now = datetime.now(timezone.utc)

    config = current_app.config_obj
    window_seconds: int = config.get("ANALYTICS_WINDOW_SECONDS", 60)
    window_minutes: int = max(1, window_seconds // 60)

    window_end: datetime = now
    window_start: datetime = now - timedelta(minutes=window_minutes)

    logger.debug(
        "analytics_diag_window_params",
        extra={
            "now": now.isoformat(),
            "window_seconds": window_seconds,
            "window_minutes": window_minutes,
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
        },
    )

    return window_minutes, window_start, window_end


def _load_samples(window_start: datetime) -> List[ReadingSample]:
    """
    Load readings from the database and convert them to ReadingSample
    instances for the pure analytics engine.
    """
    rows: List[LogExpReading] = (
        LogExpReading.query.filter(LogExpReading.timestamp >= window_start)
        .order_by(LogExpReading.timestamp.asc())
        .all()
    )

    logger.debug(
        "analytics_diag_samples_loaded",
        extra={
            "window_start": window_start.isoformat(),
            "row_count": len(rows),
        },
    )

    return [
        ReadingSample(timestamp=row.timestamp_dt, value=float(row.counts_per_second))
        for row in rows
    ]


def summarize_readings(readings: List[LogExpReading]) -> Dict[str, Any]:
    """
    Summarize a list of LogExpReading objects into JSON-safe analytics metrics.

    This is the legacy helper used by diagnostics routes. It does NOT load
    from the database; it operates only on the provided readings list.
    """
    if not readings:
        logger.debug("analytics_diag_summarize_empty")
        return {
            "window_minutes": 0,
            "count": 0,
            "window_start": None,
            "window_end": None,
            "average": None,
            "minimum": None,
            "maximum": None,
        }

    timestamps = [r.timestamp_dt for r in readings]
    window_start = min(timestamps)
    window_end = max(timestamps)

    logger.debug(
        "analytics_diag_summarize_bounds",
        extra={
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "count": len(readings),
        },
    )

    samples = [
        ReadingSample(timestamp=r.timestamp_dt, value=float(r.counts_per_second))
        for r in readings
    ]

    window_minutes = max(1, int((window_end - window_start).total_seconds() // 60))
    engine = AnalyticsEngine(window_minutes=window_minutes)
    engine.add_readings(samples)
    result = engine.compute_metrics(now=window_end)

    logger.debug(
        "analytics_diag_summarize_metrics",
        extra={
            "window_minutes": result.window_minutes,
            "count": result.count,
            "average": result.average,
            "minimum": result.minimum,
            "maximum": result.maximum,
        },
    )

    return {
        "window_minutes": result.window_minutes,
        "count": result.count,
        "window_start": result.window_start.isoformat(),
        "window_end": result.window_end.isoformat(),
        "average": result.average,
        "minimum": result.minimum,
        "maximum": result.maximum,
    }


def get_analytics_status(now: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Flask-aware analytics diagnostics for the unified /api/diagnostics payload.

    Delegates to the pure analytics diagnostics function, which returns a
    JSON-safe dict with the same fields as summarize_readings, but is
    structured around the pure engine's AnalyticsResult dataclass.

    Accepts an optional `now` for deterministic tests.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    logger.debug(
        "analytics_diag_status_requested",
        extra={"now": now.isoformat()},
    )

    window_minutes, window_start, _ = _get_window_params(now=now)
    samples: List[ReadingSample] = _load_samples(window_start=window_start)

    payload = pure_analytics_status(
        window_minutes=window_minutes,
        samples=samples,
        now=now,
    )

    logger.debug(
        "analytics_diag_status_completed",
        extra={
            "window_minutes": window_minutes,
            "sample_count": len(samples),
        },
    )

    return payload
