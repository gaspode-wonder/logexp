# tests/test_analytics.py

# Deterministic analytics tests for Step‑12D.
# Pure analytics: no ingestion, no poller, no serial, no DB writes.


def test_empty_window_returns_empty(analytics_engine, ts_base):
    result = analytics_engine.run(now=ts_base, readings=[])
    assert result == []


def test_single_reading_in_window(analytics_engine, ts_base, make_reading):
    reading = make_reading(ts_base, 10.0)
    result = analytics_engine.run(now=ts_base, readings=[reading])
    assert len(result) == 1
    assert result[0].value == 10.0


def test_reading_outside_window_excluded(analytics_engine, ts_base, shift, make_reading):
    old = make_reading(shift(ts_base, -600), 5.0)  # 10 minutes old
    new = make_reading(shift(ts_base, -100), 9.0)  # inside 5‑min window

    result = analytics_engine.run(now=ts_base, readings=[old, new])

    assert len(result) == 1
    assert result[0].value == 9.0


def test_multiple_readings_sorted_by_timestamp(analytics_engine, ts_base, shift, make_batch):
    readings = make_batch(
        [
            (shift(ts_base, -10), 3.0),
            (shift(ts_base, -5), 4.0),
            (shift(ts_base, -1), 5.0),
        ]
    )

    result = analytics_engine.run(now=ts_base, readings=readings)

    assert [r.value for r in result] == [3.0, 4.0, 5.0]


def test_window_boundary_inclusive(analytics_engine, ts_base, shift, make_reading):
    # Window = 300 seconds (5 minutes)
    boundary_ts = shift(ts_base, -300)
    r = make_reading(boundary_ts, 7.0)

    result = analytics_engine.run(now=ts_base, readings=[r])

    assert len(result) == 1
    assert result[0].value == 7.0


def test_window_boundary_exclusive(analytics_engine, ts_base, shift, make_reading):
    # Just outside the window
    outside_ts = shift(ts_base, -301)
    r = make_reading(outside_ts, 2.0)

    result = analytics_engine.run(now=ts_base, readings=[r])

    assert result == []


def test_mixed_window_behavior(analytics_engine, ts_base, shift, make_batch):
    readings = make_batch(
        [
            (shift(ts_base, -1000), 1.0),  # too old
            (shift(ts_base, -200), 2.0),  # inside
            (shift(ts_base, -50), 3.0),  # inside
        ]
    )

    result = analytics_engine.run(now=ts_base, readings=readings)

    assert [r.value for r in result] == [2.0, 3.0]
