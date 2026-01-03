# filename: logexp/analytics/api.py

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .engine import AnalyticsEngine, AnalyticsResult


def analyze(
    samples: Iterable[float], window_minutes: int, now: datetime
) -> AnalyticsResult:
    """
    Typed wrapper around AnalyticsEngine.analyze.
    Ensures the return type is AnalyticsResult for mypy.
    """
    result = AnalyticsEngine.analyze(samples, window_minutes, now)
    assert isinstance(result, AnalyticsResult)
    return result
