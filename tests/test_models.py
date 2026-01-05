from datetime import datetime

import pytest
from flask import Flask

from logexp.app.config import load_config
from logexp.app.models import LogExpReading
from logexp.seeds.seed_data import seed_test_data


@pytest.fixture
def app():
    app = Flask(__name__)

    # Attach a proper config object
    app.config_obj = load_config(
        overrides={
            "LOCAL_TIMEZONE": "America/Chicago",
            "TESTING": True,
            "START_POLLER": False,
        }
    )

    return app


def test_to_dict_returns_expected_fields(app):
    # Arrange: create a sample reading
    reading = LogExpReading(
        id=1,
        timestamp=datetime(2025, 12, 6, 19, 52),  # naive datetime
        counts_per_second=0.15,
        counts_per_minute=9.0,
        microsieverts_per_hour=0.05,
        mode="normal",
    )

    # Act: call to_dict inside app context
    with app.app_context():
        result = reading.to_dict()

    # Assert: all expected keys are present
    expected_keys = {
        "id",
        "timestamp",
        "counts_per_second",
        "counts_per_minute",
        "microsieverts_per_hour",
        "mode",
    }
    assert set(result.keys()) == expected_keys

    # Assert: timestamp is a datetime object localized to America/Chicago
    assert isinstance(result["timestamp"], datetime)
    assert result["timestamp"].tzinfo is not None
    assert result["timestamp"].tzinfo.key == "America/Chicago"

    # Assert: numeric fields match
    assert result["counts_per_second"] == 0.15
    assert result["counts_per_minute"] == 9.0
    assert result["microsieverts_per_hour"] == 0.05
    assert result["mode"] == "normal"


def test_logexp_reading_model(test_app, db_session):
    seed_test_data(test_app)  # insert row

    # Query using the active test session
    result = db_session.query(LogExpReading).first()

    assert result.counts_per_second == 1
    assert result.counts_per_minute == 60
    assert result.microsieverts_per_hour == 0.01
    assert result.mode == "test"
