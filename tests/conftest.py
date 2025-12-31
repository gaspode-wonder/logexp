import pytest

from logexp.app import create_app
from logexp.app.extensions import db


@pytest.fixture(scope="session")
def test_app():
    app = create_app(
        {
            "TESTING": True,
            "START_POLLER": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
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
