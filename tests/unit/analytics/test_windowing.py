# logexp/tests/unit/analytics/test_windowing.py

import datetime as dt

from logexp.analytics.engine import AnalyticsEngine, ReadingSample


def test_empty_window_returns_empty():
    engine = AnalyticsEngine(window_minutes=5)
    now = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    assert engine.get_window(now) == []


def test_in_window_sample_included():
    engine = AnalyticsEngine(window_minutes=5)
    now = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    sample = ReadingSample(timestamp=now, value=10.0)
    engine.add_reading(sample)

    result = engine.get_window(now)
    assert len(result) == 1
    assert result[0].value == 10.0


def test_outside_window_excluded():
    engine = AnalyticsEngine(window_minutes=5)
    now = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    old = ReadingSample(timestamp=now - dt.timedelta(minutes=10), value=5.0)
    engine.add_reading(old)

    assert engine.get_window(now) == []
