# filename: tests/conftest.py

"""
Global pytest fixtures for LogExp.

Ensures:
- Flask app + DB fixtures are available
- analytics + poller fixtures are imported
- reading_factory is available
"""

# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------
import pytest
from freezegun import freeze_time

# ---------------------------------------------------------------------------
# Application imports
# ---------------------------------------------------------------------------
from logexp.app import create_app
from logexp.app.extensions import db

# ---------------------------------------------------------------------------
# Fixture imports (import NAMES, not modules)
# These imports are intentionally unused — pytest registers fixtures by name.
# Ruff must be silenced with noqa: F401.
# ---------------------------------------------------------------------------
from tests.fixtures.reading_factory import (  # noqa: F401
    reading_factory,
    make_reading,
    make_batch,
)

from tests.fixtures.analytics_engine import analytics_engine  # noqa: F401
from tests.fixtures.analytics import ts_base, shift  # noqa: F401
from tests.fixtures.poller_factory import make_poller  # noqa: F401


# ---------------------------------------------------------------------------
# Flask application fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def test_app():
    """
    Create a fresh Flask app + DB schema for each test.
    """
    app = create_app(
        {
            "TESTING": True,
            "START_POLLER": False,
            "ANALYTICS_ENABLED": True,
            "ANALYTICS_WINDOW_SECONDS": 60,
            "LOCAL_TIMEZONE": "UTC",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(test_app):
    """
    Provide a clean SQLAlchemy session per test.
    """
    with test_app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        yield db.session

        db.session.rollback()


@pytest.fixture(scope="function")
def test_client(test_app):
    """
    Provide a Flask test client.
    """
    return test_app.test_client()


# ---------------------------------------------------------------------------
# Time freezer
# ---------------------------------------------------------------------------


@pytest.fixture
def freezer():
    """
    Time-freezing fixture for deterministic diagnostics tests.
    """
    with freeze_time() as frozen:
        yield frozen
