import os
import pytest
from flask import Flask
from logexp.app import db, create_app

@pytest.fixture(scope="session")
def test_app():
    """Create a Flask app configured for testing with in-memory SQLite."""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "LOCAL_TIMEZONE": "US/Central",  # ensure timezone is set for to_dict()
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def test_client(test_app):
    """Provide a test client for routes."""
    return test_app.test_client()

@pytest.fixture(scope="function")
def db_session(test_app):
    """Provide a clean database session per test."""
    with test_app.app_context():
        yield db.session
        db.session.rollback()
