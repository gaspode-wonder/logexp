# logexp/tests/unit/analytics/test_engine_state.py

import datetime as dt

from logexp.analytics.engine import AnalyticsEngine, ReadingSample


def test_engine_accumulates_samples():
    engine = AnalyticsEngine(window_minutes=5)
    now = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    engine.add_reading(ReadingSample(timestamp=now, value=1.0))
    engine.add_reading(ReadingSample(timestamp=now, value=2.0))

    assert len(engine._samples) == 2
