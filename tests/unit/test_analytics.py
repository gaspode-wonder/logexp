# tests/unit/test_analytics.py

import datetime

from logexp.app.analytics import compute_window, run_analytics
from logexp.app.extensions import db


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
    """
    with test_app.app_context():
        now = datetime.datetime.now(datetime.timezone.utc)

        # inside window (default window = 60s)
        reading_factory(now - datetime.timedelta(seconds=30), cps=10)

        # outside window
        reading_factory(now - datetime.timedelta(seconds=120), cps=20)

        db.session.commit()

        readings = compute_window()
        assert len(readings) == 1
        assert readings[0].counts_per_second == 10


def test_rollup_average(test_app, reading_factory):
    """
    Rollup should compute a correct average CPS.
    """
    with test_app.app_context():
        now = datetime.datetime.now(datetime.timezone.utc)

        reading_factory(now, cps=10)
        reading_factory(now + datetime.timedelta(seconds=1), cps=20)
        reading_factory(now + datetime.timedelta(seconds=2), cps=30)

        db.session.commit()

        result = run_analytics()

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
        now = datetime.datetime.now(datetime.timezone.utc)

        reading_factory(now + datetime.timedelta(seconds=2), cps=30)
        reading_factory(now, cps=10)
        reading_factory(now + datetime.timedelta(seconds=1), cps=20)

        db.session.commit()

        result = run_analytics()

        assert result["count"] == 3
        assert result["first_timestamp"] < result["last_timestamp"]
