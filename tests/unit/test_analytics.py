# filename: tests/unit/test_analytics.py
# Deterministic DB‑backed analytics tests for Step‑12D.
# No datetime.now(). No implicit nondeterminism. No passing now=.

import datetime

from app.extensions import db
from app.services.analytics import compute_window, run_analytics

FIXED_NOW = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)


def test_empty_window_returns_none(test_app):
    """
    If no readings exist, analytics should return None.
    """
    with test_app.app_context():
        result = run_analytics()
        assert result is None


def test_window_boundary_inclusion(test_app, reading_factory):
    """
    Only readings inside the configured analytics window should be included.
    Default window = 60 seconds.
    """
    with test_app.app_context():
        inside = FIXED_NOW - datetime.timedelta(seconds=30)
        outside = FIXED_NOW - datetime.timedelta(seconds=120)

        reading_factory(inside, cps=10)
        reading_factory(outside, cps=20)

        db.session.commit()

        readings = compute_window()
        assert len(readings) == 1
        assert readings[0].counts_per_second == 10


def test_rollup_average(test_app, reading_factory):
    """
    Rollup should compute a correct average CPS.
    """
    with test_app.app_context():
        t0 = FIXED_NOW
        t1 = FIXED_NOW + datetime.timedelta(seconds=1)
        t2 = FIXED_NOW + datetime.timedelta(seconds=2)

        reading_factory(t0, cps=10)
        reading_factory(t1, cps=20)
        reading_factory(t2, cps=30)

        db.session.commit()

        result = run_analytics()

        result = run_analytics()
        assert result is not None
        assert result["count"] == 3
        assert result["avg_cps"] == 20


def test_analytics_disabled(test_app):
    """
    If analytics is disabled via config, run_analytics should return None.
    """
    with test_app.app_context():
        test_app.config_obj["ANALYTICS_ENABLED"] = False
        result = run_analytics()
        assert result is None


def test_out_of_order_readings(test_app, reading_factory):
    """
    Analytics should handle out-of-order readings and return sorted timestamps.
    """
    with test_app.app_context():
        t0 = FIXED_NOW
        t1 = FIXED_NOW + datetime.timedelta(seconds=1)
        t2 = FIXED_NOW + datetime.timedelta(seconds=2)

        # Insert out of order
        reading_factory(t2, cps=30)
        reading_factory(t0, cps=10)
        reading_factory(t1, cps=20)

        db.session.commit()

        result = run_analytics()
        assert result is not None
        assert result["first_timestamp"] < result["last_timestamp"]
