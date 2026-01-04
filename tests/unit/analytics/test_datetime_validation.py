# tests/unit/analytics/test_datetime_validation.py

import datetime as dt
import pytest

from logexp.analytics.engine import AnalyticsEngine, ReadingSample


def test_rejects_naive_datetime():
    engine = AnalyticsEngine(window_minutes=5)
    naive = dt.datetime(2025, 1, 1, 12, 0, 0)

    with pytest.raises(ValueError):
        engine.add_reading(ReadingSample(timestamp=naive, value=1.0))


def test_rejects_naive_now():
    engine = AnalyticsEngine(window_minutes=5)
    naive_now = dt.datetime(2025, 1, 1, 12, 0, 0)

    with pytest.raises(ValueError):
        engine.get_window(naive_now)
