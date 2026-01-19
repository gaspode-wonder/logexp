# filename: logexp/analytics/api.py

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from app.logging_setup import get_logger

from .engine import AnalyticsEngine, AnalyticsResult, ReadingSample

logger = get_logger("logexp.analytics")


def analyze(
    samples: Iterable[float],
    window_minutes: int,
    now: datetime,
) -> AnalyticsResult:
    """
    Typed wrapper around the analytics engine.

    Historically this attempted to call `AnalyticsEngine.analyze(...)`,
    but that method does not exist. The correct behavior is to instantiate
    an engine, convert raw values into ReadingSample objects, add them,
    compute metrics, and return an AnalyticsResult.
    """
    logger.debug(
        "analytics_api_analyze_called",
        extra={
            "window_minutes": window_minutes,
            "sample_count": len(list(samples)) if hasattr(samples, "__len__") else None,
            "now": now.isoformat(),
        },
    )

    engine = AnalyticsEngine(window_minutes=window_minutes)

    # Convert raw floats into ReadingSample objects using the provided timestamp.
    reading_samples: List[ReadingSample] = [
        ReadingSample(timestamp=now, value=float(v)) for v in samples
    ]

    engine.add_readings(reading_samples)
    result: AnalyticsResult = engine.compute_metrics(now=now)

    logger.debug(
        "analytics_api_analyze_completed",
        extra={
            "count": result.count,
            "average": result.average,
            "minimum": result.minimum,
            "maximum": result.maximum,
            "window_start": result.window_start.isoformat(),
            "window_end": result.window_end.isoformat(),
        },
    )

    return result
