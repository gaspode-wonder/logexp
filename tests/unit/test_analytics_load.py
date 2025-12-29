# tests/unit/test_analytics_load.py
"""
Load-focused tests for analytics behavior under higher reading volume.
"""

from datetime import timedelta

from logexp.app.analytics import run_analytics
from logexp.app.extensions import db


def test_high_volume_readings(analytics_app, frozen_now, reading_factory, db_session):
    now = frozen_now

    for i in range(1000):
        reading_factory(now - timedelta(seconds=i % 30), cps=i % 50)

    db.session.commit()

    result = run_analytics(now=now)
    assert result is not None
    assert result["count"] > 0


def test_randomized_timestamps(analytics_app, frozen_now, reading_factory, db_session):
    now = frozen_now

    for i in range(200):
        reading_factory(now - timedelta(seconds=i % 45), cps=i % 10)

    db.session.commit()

    result = run_analytics(now=now)
    assert result is not None
    assert result["count"] > 0


def test_large_window(analytics_app, frozen_now, reading_factory, db_session):
    from flask import current_app

    now = frozen_now
    current_app.config_obj["ANALYTICS_WINDOW_SECONDS"] = 3600

    for i in range(300):
        reading_factory(now - timedelta(seconds=i * 5), cps=5)

    db.session.commit()

    result = run_analytics(now=now)
    assert result is not None
    assert result["count"] == 300


def test_exact_cutoff_boundary(analytics_app, frozen_now, reading_factory, db_session):
    from flask import current_app

    now = frozen_now
    window = 60
    current_app.config_obj["ANALYTICS_WINDOW_SECONDS"] = window

    # exactly at cutoff
    reading_factory(now - timedelta(seconds=window), cps=10)

    db.session.commit()

    result = run_analytics(now=now)
    assert result is not None
    assert result["count"] == 1


def test_mixed_cps_values(analytics_app, frozen_now, reading_factory, db_session):
    now = frozen_now

    reading_factory(now, cps=5)
    reading_factory(now + timedelta(seconds=1), cps=15)
    reading_factory(now + timedelta(seconds=2), cps=25)

    db.session.commit()

    result = run_analytics(now=now)

    assert result is not None
    assert result["avg_cps"] == 15
