# FILE: tests/conftest.py

import pytest

from logexp.app import create_app
from logexp.app.extensions import db
from tests.fixtures.reading_factory import create_reading


@pytest.fixture
def reading_factory():
    return create_reading


@pytest.fixture(scope="function")
def test_app():
    """
    Each test gets a completely fresh Flask app, config_obj, and database.
    No state leaks between tests.
    """

    app = create_app(
        overrides={
            "TESTING": True,
            "START_POLLER": False,
            # In-memory SQLite; datetime is handled in Python as ISO8601 strings.
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "INGESTION_ENABLED": True,
            "ANALYTICS_ENABLED": True,
            "ANALYTICS_WINDOW_SECONDS": 60,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(scope="function")
def test_client(test_app):
    return test_app.test_client()
