# tests/unit/analytics/test_metrics.py

import datetime as dt

from logexp.analytics.engine import AnalyticsEngine, ReadingSample


def test_metrics_empty_window():
    engine = AnalyticsEngine(window_minutes=5)
    now = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    result = engine.compute_metrics(now)

    assert result.count == 0
    assert result.average is None
    assert result.minimum is None
    assert result.maximum is None


def test_metrics_basic_stats():
    engine = AnalyticsEngine(window_minutes=5)
    now = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    samples = [
        ReadingSample(timestamp=now - dt.timedelta(seconds=10), value=3.0),
        ReadingSample(timestamp=now - dt.timedelta(seconds=5), value=7.0),
    ]
    engine.add_readings(samples)

    result = engine.compute_metrics(now)

    assert result.count == 2
    assert result.minimum == 3.0
    assert result.maximum == 7.0
    assert result.average == 5.0
