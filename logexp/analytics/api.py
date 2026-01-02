# logexp/analytics/api.py

from datetime import datetime
from typing import List

from .engine import AnalyticsEngine, ReadingSample


def compute_window(samples: List[ReadingSample], window_minutes: int, now: datetime):
    """
    Legacy pure API wrapper around the analytics engine.
    """
    return AnalyticsEngine.analyze(samples, window_minutes, now)
