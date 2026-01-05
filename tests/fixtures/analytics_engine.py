# filename: tests/fixtures/analytics_engine.py

"""
Fixtures for the pure AnalyticsEngine.
"""

from datetime import datetime, timedelta, timezone

import pytest

from logexp.analytics.engine import AnalyticsEngine, ReadingSample


@pytest.fixture
def analytics_engine():
    """
    Fresh AnalyticsEngine with a 5-minute window, matching test expectations.
    """
    return AnalyticsEngine(window_minutes=5)


@pytest.fixture
def make_reading():
    """
    Factory for creating timezone-aware ReadingSample objects.
    """

    def _make(ts, value):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ReadingSample(timestamp=ts, value=value)

    return _make


@pytest.fixture
def ts_base():
    """
    Base timestamp used by analytics tests.
    """
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def shift():
    """
    shift(base, seconds=-10) → base - 10 seconds
    """

    def _shift(base, seconds=0, minutes=0):
        return base + timedelta(seconds=seconds, minutes=minutes)

    return _shift


@pytest.fixture
def make_batch(make_reading):
    """
    Create a batch of readings from (timestamp, value) tuples.
    """

    def _make(pairs):
        return [make_reading(ts, val) for ts, val in pairs]

    return _make
