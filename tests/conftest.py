import pytest
from logexp.app import create_app
from logexp.app.config import load_config
from logexp.app.extensions import db


@pytest.fixture(scope="session")
def test_app():
    # Create the app normally
    app = create_app()

    # Override config for testing
    app.config_obj = load_config(overrides={
        "TESTING": True,
        "START_POLLER": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    # Apply DB URI to Flask config (SQLAlchemy requires this)
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config_obj["SQLALCHEMY_DATABASE_URI"]

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(test_app):
    with test_app.app_context():
        # Clean all tables before each test
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        yield db.session

        # Roll back any uncommitted changes
        db.session.rollback()


@pytest.fixture(scope="function")
def test_client(test_app):
    return test_app.test_client()