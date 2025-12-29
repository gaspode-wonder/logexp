# tests/unit/test_analytics.py
"""
Unit tests for analytics windowing and rollup behavior.
"""

from datetime import timedelta

from logexp.app.analytics import run_analytics, compute_window
from logexp.app.extensions import db


def test_empty_window_returns_none(analytics_app, frozen_now, db_session):
    now = frozen_now
    result = run_analytics(now=now)
    assert result is None


def test_window_boundary_inclusion(analytics_app, frozen_now, reading_factory, db_session):
    """
    Only readings at or after the cutoff should be included.
    """
    now = frozen_now

    # Inside window (default 60s)
    reading_factory(now - timedelta(seconds=30), cps=10)

    # Outside window
    reading_factory(now - timedelta(seconds=120), cps=20)

    db.session.commit()

    readings = compute_window(now=now)
    assert len(readings) == 1
    assert readings[0].counts_per_second == 10


def test_rollup_average(analytics_app, frozen_now, reading_factory, db_session):
    """
    Average CPS should be computed over the window readings.
    """
    now = frozen_now

    reading_factory(now, cps=10)
    reading_factory(now + timedelta(seconds=1), cps=20)
    reading_factory(now + timedelta(seconds=2), cps=30)

    db.session.commit()

    result = run_analytics(now=now)

    assert result is not None
    assert result["count"] == 3
    assert result["avg_cps"] == 20


def test_analytics_disabled(analytics_app, frozen_now, db_session):
    from flask import current_app

    now = frozen_now
    current_app.config_obj["ANALYTICS_ENABLED"] = False

    result = run_analytics(now=now)
    assert result is None


def test_out_of_order_readings(analytics_app, frozen_now, reading_factory, db_session):
    """
    Result timestamps should have a sensible first/last ordering
    even if inserts are out of order.
    """
    now = frozen_now

    reading_factory(now + timedelta(seconds=2), cps=30)
    reading_factory(now, cps=10)
    reading_factory(now + timedelta(seconds=1), cps=20)

    db.session.commit()

    result = run_analytics(now=now)

    assert result is not None
    assert result["count"] == 3
    assert result["first_timestamp"] < result["last_timestamp"]
