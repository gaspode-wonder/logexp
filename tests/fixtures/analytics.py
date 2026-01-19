# tests/fixtures/analytics.py

import datetime as dt

import pytest

from analytics.engine import AnalyticsEngine, ReadingSample


@pytest.fixture
def ts_base() -> dt.datetime:
    """Deterministic anchor timestamp for analytics tests."""
    return dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)


@pytest.fixture
def shift():
    """Shift a timestamp by N seconds."""

    def _shift(ts: dt.datetime, seconds: int) -> dt.datetime:
        return ts + dt.timedelta(seconds=seconds)

    return _shift


@pytest.fixture
def make_sample():
    """Create a ReadingSample with explicit timestamp and value."""

    def _make(ts: dt.datetime, value: float) -> ReadingSample:
        return ReadingSample(timestamp=ts, value=value)

    return _make


@pytest.fixture
def make_batch(make_sample):
    """Create a list of ReadingSample objects from (ts, value) pairs."""

    def _batch(pairs):
        return [make_sample(ts, value) for ts, value in pairs]

    return _batch


@pytest.fixture
def analytics_engine():
    """
    Deterministic analytics engine with a fixed 5‑minute window.
    No ingestion, no poller, no DB.
    """
    return AnalyticsEngine(window_minutes=5)
