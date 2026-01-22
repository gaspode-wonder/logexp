# filename: logexp/tests/unit/test_analytics_load.py
# Deterministic DB‑backed analytics load tests for Step‑12D.
# No datetime.now(), no randomness, no implicit windows.

import datetime

from logexp.app.extensions import db
from logexp.app.services.analytics import compute_window, run_analytics

FIXED_NOW = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)


def test_high_volume_readings(test_app, reading_factory):
    """
    Analytics should handle large numbers of readings deterministically.
    """
    with test_app.app_context():
        # Ensure analytics uses the correct window
        test_app.config["ANALYTICS_WINDOW_SECONDS"] = 120

        # 1000 readings inside a 120‑second window
        for i in range(1000):
            ts = FIXED_NOW - datetime.timedelta(seconds=i % 120)
            cps = (i % 100) + 1
            reading_factory(ts, cps=cps)

        db.session.commit()

        result = run_analytics()
        assert result is not None
        assert result["count"] == 1000


def test_randomized_timestamps(test_app, reading_factory):
    """
    Analytics should correctly sort and process out‑of‑order timestamps.
    Deterministic version: fixed timestamps, shuffled manually.
    """
    with test_app.app_context():
        window = test_app.config["ANALYTICS_WINDOW_SECONDS"]

        timestamps = [FIXED_NOW - datetime.timedelta(seconds=i) for i in range(window - 1)]

        # Deterministic shuffle: reverse order
        timestamps = list(reversed(timestamps))

        for ts in timestamps:
            reading_factory(ts, cps=10)

        db.session.commit()

        result = run_analytics()
        assert result is not None
        assert result["count"] == len(timestamps)
        assert result["first_timestamp"] < result["last_timestamp"]


def test_large_window(test_app, reading_factory):
    """
    Analytics should respect large window sizes deterministically.
    """
    with test_app.app_context():
        test_app.config["ANALYTICS_WINDOW_SECONDS"] = 3600  # 1 hour

        # 300 readings spread across 3500 seconds
        for i in range(300):
            ts = FIXED_NOW - datetime.timedelta(seconds=i * 10)
            reading_factory(ts, cps=5)

        db.session.commit()

        result = run_analytics()
        assert result is not None
        assert result["count"] > 0


def test_exact_cutoff_boundary(test_app, reading_factory):
    """
    A reading exactly at the cutoff timestamp should be included.
    """
    with test_app.app_context():
        window = test_app.config["ANALYTICS_WINDOW_SECONDS"]

        inside = FIXED_NOW - datetime.timedelta(seconds=window)
        outside = FIXED_NOW - datetime.timedelta(seconds=window + 1)

        reading_factory(inside, cps=10)
        reading_factory(outside, cps=20)

        db.session.commit()

        readings = compute_window(now=FIXED_NOW)
        assert len(readings) == 1
        assert readings[0].counts_per_second == 10


def test_mixed_cps_values(test_app, reading_factory):
    """
    Analytics should compute correct averages deterministically.
    """
    with test_app.app_context():
        values = [1, 5, 10, 50, 100, 200, 500]

        for v in values:
            reading_factory(FIXED_NOW, cps=v)

        db.session.commit()

        result = run_analytics()
        assert result is not None
        assert result["avg_cps"] == sum(values) / len(values)
