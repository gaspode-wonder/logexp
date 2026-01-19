# FILE: tests/test_analytics_engine.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from analytics.engine import AnalyticsEngine, AnalyticsResult, ReadingSample


@pytest.fixture
def fixed_now() -> datetime:
    """
    A fixed point in time used for deterministic analytics tests.
    """
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def engine_10_min_window() -> AnalyticsEngine:
    """
    Analytics engine with a fixed 10-minute window for deterministic behavior.
    """
    return AnalyticsEngine(window_minutes=10)


def _sample_at(offset_minutes: int, base: datetime, value: float) -> ReadingSample:
    return ReadingSample(timestamp=base + timedelta(minutes=offset_minutes), value=value)


def test_empty_window_produces_zero_count_and_none_metrics(
    engine_10_min_window: AnalyticsEngine,
    fixed_now: datetime,
) -> None:
    result = engine_10_min_window.compute_metrics(now=fixed_now)

    assert isinstance(result, AnalyticsResult)
    assert result.count == 0
    assert result.average is None
    assert result.minimum is None
    assert result.maximum is None
    assert result.window_end == fixed_now
    assert result.window_start == fixed_now - timedelta(minutes=10)


def test_readings_within_window_are_included(
    engine_10_min_window: AnalyticsEngine,
    fixed_now: datetime,
) -> None:
    # Window is from fixed_now - 10 minutes to fixed_now.
    # These three are within that window.
    samples = [
        _sample_at(-9, fixed_now, 1.0),
        _sample_at(-5, fixed_now, 2.0),
        _sample_at(-1, fixed_now, 3.0),
    ]
    engine_10_min_window.add_readings(samples)

    window = engine_10_min_window.get_window(now=fixed_now)
    assert len(window) == 3
    assert [s.value for s in window] == [1.0, 2.0, 3.0]


def test_readings_outside_window_are_excluded(
    engine_10_min_window: AnalyticsEngine,
    fixed_now: datetime,
) -> None:
    # Two older readings (outside the 10-minute window) and one inside.
    samples = [
        _sample_at(-30, fixed_now, 10.0),
        _sample_at(-20, fixed_now, 20.0),
        _sample_at(-5, fixed_now, 30.0),
    ]
    engine_10_min_window.add_readings(samples)

    window = engine_10_min_window.get_window(now=fixed_now)
    assert len(window) == 1
    assert window[0].value == 30.0


def test_window_boundary_inclusive_on_start_and_end(
    engine_10_min_window: AnalyticsEngine,
    fixed_now: datetime,
) -> None:
    # exactly at start boundary (fixed_now - 10) and end boundary (fixed_now)
    samples = [
        _sample_at(-10, fixed_now, 1.0),
        _sample_at(0, fixed_now, 2.0),
    ]
    engine_10_min_window.add_readings(samples)

    window = engine_10_min_window.get_window(now=fixed_now)
    assert len(window) == 2
    assert {s.value for s in window} == {1.0, 2.0}


def test_compute_metrics_uses_only_window_samples(
    engine_10_min_window: AnalyticsEngine,
    fixed_now: datetime,
) -> None:
    # two samples in window, one outside
    samples = [
        _sample_at(-9, fixed_now, 1.0),
        _sample_at(-5, fixed_now, 3.0),
        _sample_at(-15, fixed_now, 100.0),
    ]
    engine_10_min_window.add_readings(samples)

    result = engine_10_min_window.compute_metrics(now=fixed_now)

    assert result.count == 2
    assert pytest.approx(result.average) == 2.0
    assert result.minimum == 1.0
    assert result.maximum == 3.0


def test_engine_rejects_naive_datetimes() -> None:
    engine = AnalyticsEngine(window_minutes=5)
    naive_ts = datetime(2024, 1, 1, 12, 0, 0)  # no tzinfo

    with pytest.raises(ValueError):
        engine.add_reading(ReadingSample(timestamp=naive_ts, value=1.0))

    with pytest.raises(ValueError):
        engine.get_window(now=naive_ts)

    with pytest.raises(ValueError):
        engine.compute_metrics(now=naive_ts)
