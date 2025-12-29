# tests/conftest.py

"""
Unified pytest fixtures for LogExp.

This file provides a single, deterministic application instance for all tests.
All database operations, analytics queries, ingestion writes, and route tests
run against the same in‑memory SQLite engine to guarantee consistency.

Fixtures included:
- frozen_now: deterministic timestamp
- test_app: unified Flask application for all tests
- analytics_app: alias of test_app for compatibility with existing tests
- db_session: clean SQLAlchemy session per test
- test_client: HTTP client for route tests
- reading_factory: helper for inserting LogExpReading rows
"""

import pytest
from datetime import datetime, timezone

from logexp.app import create_app
from logexp.app.extensions import db
from logexp.app.models import LogExpReading
from logexp.app.logging_loader import configure_logging


# ---------------------------------------------------------------------------
# Deterministic timestamp fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def frozen_now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Unified application fixture (single app for ALL tests)
# ---------------------------------------------------------------------------
@pytest.fixture
def test_app():
    """
    Full application used by all tests: routes, ingestion, analytics, models.
    Uses an in‑memory SQLite database and disables the poller.
    """
    app = create_app({
        "TESTING": True,
        "START_POLLER": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "ANALYTICS_ENABLED": True,
        "INGESTION_ENABLED": True,
        "ANALYTICS_WINDOW_SECONDS": 60,
    })

    # ⭐ Logging MUST be configured inside the same app context tests will use
    with app.app_context():
        configure_logging(app)
        db.create_all()

    return app


# ---------------------------------------------------------------------------
# Analytics-enabled application fixture (alias of test_app)
# ---------------------------------------------------------------------------
@pytest.fixture
def analytics_app(test_app):
    """
    Compatibility fixture required by the analytics test suite.
    This is intentionally the same object as test_app.
    """
    return test_app


# ---------------------------------------------------------------------------
# Database session fixture (single session for ALL tests)
# ---------------------------------------------------------------------------
@pytest.fixture
def db_session(test_app):
    """
    Provides a clean SQLAlchemy session tied to test_app.
    Ensures each test begins with an empty database state.
    """
    with test_app.app_context():
        # Clean all tables before each test
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        yield db.session

        db.session.rollback()


# ---------------------------------------------------------------------------
# Test client fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


# ---------------------------------------------------------------------------
# Reading factory fixture (uses the SAME db_session)
# ---------------------------------------------------------------------------
@pytest.fixture
def reading_factory(db_session):
    """
    Creates LogExpReading rows using the unified db_session.
    Does not commit automatically; tests control commit boundaries.
    """

    def _factory(ts, cps=10, mode="test"):
        reading = LogExpReading(
            timestamp=ts.isoformat(),
            counts_per_second=cps,
            counts_per_minute=cps * 60,
            microsieverts_per_hour=0.01,
            mode=mode,
        )
        db_session.add(reading)
        return reading

    return _factory
