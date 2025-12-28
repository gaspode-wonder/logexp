# tests/conftest.py

import pytest
from logexp.app import create_app
from logexp.app.config import load_config
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
    app = create_app()

    # Deterministic test config
    app.config_obj = load_config(overrides={
        "TESTING": True,
        "START_POLLER": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "INGESTION_ENABLED": True,   # ensure clean default for each test
    })

    # SQLAlchemy requires this on the Flask config
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config_obj["SQLALCHEMY_DATABASE_URI"]

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(test_app):
    """
    Provides a clean SQLAlchemy session tied to the fresh app.
    """
    with test_app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(scope="function")
def test_client(test_app):
    return test_app.test_client()
