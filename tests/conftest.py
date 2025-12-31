# tests/conftest.py
import pytest

from logexp.app import create_app
from logexp.app.extensions import db
from tests.fixtures.reading_factory import reading_factory


@pytest.fixture(scope="function")
def test_app():
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
    with test_app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        yield db.session

        db.session.rollback()


@pytest.fixture(scope="function")
def test_client(test_app):
    return test_app.test_client()
