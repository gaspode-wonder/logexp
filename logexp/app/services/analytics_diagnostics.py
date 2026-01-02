# logexp/app/services/analytics_diagnostics.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from flask import current_app

from logexp.analytics.diagnostics import (
    get_analytics_status as pure_analytics_status,
)
from logexp.analytics.engine import AnalyticsEngine, ReadingSample
from logexp.app.models import Reading


def _get_window_params(
    now: Optional[datetime] = None,
) -> tuple[int, datetime, datetime]:
    """
    Derive window parameters from config and the current time.

    Returns:
        (window_minutes, window_start, window_end)
    """
    if now is None:
        now = datetime.now(timezone.utc)

    config = current_app.config_obj
    window_seconds = config.get("ANALYTICS_WINDOW_SECONDS", 60)
    window_minutes = max(1, window_seconds // 60)

    window_end = now
    window_start = now - timedelta(minutes=window_minutes)

    return window_minutes, window_start, window_end


def _load_samples(window_start: datetime) -> List[ReadingSample]:
    """
    Load readings from the database and convert them to ReadingSample
    instances for the pure analytics engine.
    """
    rows = (
        Reading.query.filter(Reading.timestamp >= window_start)
        .order_by(Reading.timestamp.asc())
        .all()
    )

    return [
        ReadingSample(timestamp=row.timestamp_dt, value=float(row.counts_per_second))
        for row in rows
    ]


def summarize_readings(now: Optional[datetime] = None) -> dict:
    """
    Legacy service-layer API used by logging and diagnostics.

    Returns a JSON-safe summary of readings over the configured window:
        - window_minutes
        - count
        - window_start (ISO8601)
        - window_end (ISO8601)
        - average
        - minimum
        - maximum

    Accepts an optional `now` to allow deterministic tests to fix time.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    window_minutes, window_start, _ = _get_window_params(now=now)
    samples = _load_samples(window_start=window_start)

    engine = AnalyticsEngine(window_minutes=window_minutes)
    engine.add_readings(samples)
    result = engine.compute_metrics(now=now)

    return {
        "window_minutes": result.window_minutes,
        "count": result.count,
        "window_start": result.window_start.isoformat(),
        "window_end": result.window_end.isoformat(),
        "average": result.average,
        "minimum": result.minimum,
        "maximum": result.maximum,
    }


def get_analytics_status(now: Optional[datetime] = None) -> dict:
    """
    Flask-aware analytics diagnostics for the unified /api/diagnostics payload.

    Delegates to the pure analytics diagnostics function, which returns a
    JSON-safe dict with the same fields as summarize_readings, but is
    structured around the pure engine's AnalyticsResult dataclass.

    Accepts an optional `now` for deterministic tests.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    window_minutes, window_start, _ = _get_window_params(now=now)
    samples = _load_samples(window_start=window_start)

    return pure_analytics_status(
        window_minutes=window_minutes,
        samples=samples,
        now=now,
    )
