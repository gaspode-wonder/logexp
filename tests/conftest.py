# tests/conftest.py
"""
Unified pytest fixtures for LogExp.

This file provides:
- test_app: full application for routes, ingestion, and integration tests
- analytics_app: minimal application for analytics-only tests
- reading_factory: automatically binds to whichever app fixture is active
- frozen_now: deterministic timestamp fixture
- db_session: clean DB session per test
"""

import pytest
from datetime import datetime, timezone

from logexp.app import create_app
from logexp.app.extensions import db
from logexp.app.models import LogExpReading


# ---------------------------------------------------------------------------
# Deterministic timestamp fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def frozen_now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Minimal analytics-only app
# ---------------------------------------------------------------------------
@pytest.fixture
def analytics_app():
    """
    Minimal app context for analytics-only tests.
    No routes, no ingestion, no poller.
    """
    app = create_app({
        "TESTING": True,
        "START_POLLER": False,
        "ANALYTICS_ENABLED": True,
        "ANALYTICS_WINDOW_SECONDS": 60,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# ---------------------------------------------------------------------------
# Full application for routes, ingestion, and integration tests
# ---------------------------------------------------------------------------
@pytest.fixture
def test_app():
    """
    Full application used by route tests, ingestion tests, and model tests.
    """
    app = create_app({
        "TESTING": True,
        "START_POLLER": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "ANALYTICS_ENABLED": True,
        "INGESTION_ENABLED": True,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# ---------------------------------------------------------------------------
# DB session fixture (works for both apps)
# ---------------------------------------------------------------------------
@pytest.fixture
def db_session(request):
    """
    Provides a clean SQLAlchemy session tied to whichever app is active.
    """
    app = (
        request.getfixturevalue("analytics_app")
        if "analytics_app" in request.fixturenames
        else request.getfixturevalue("test_app")
    )

    with app.app_context():
        # Clean all tables before each test
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        yield db.session

        db.session.rollback()


# ---------------------------------------------------------------------------
# Test client (only valid for test_app)
# ---------------------------------------------------------------------------
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


# ---------------------------------------------------------------------------
# Reading factory that binds to the active app
# ---------------------------------------------------------------------------
@pytest.fixture
def reading_factory(request):
    """
    Creates LogExpReading rows bound to whichever app fixture is active.
    """
    # Determine which app this test is using
    app = (
        request.getfixturevalue("analytics_app")
        if "analytics_app" in request.fixturenames
        else request.getfixturevalue("test_app")
    )

    def _factory(ts, cps=10, mode="test"):
        with app.app_context():
            r = LogExpReading(
                timestamp=ts.isoformat(),
                counts_per_second=cps,
                counts_per_minute=cps * 60,
                microsieverts_per_hour=0.01,
                mode=mode,
            )
            db.session.add(r)
            return r

    return _factory
