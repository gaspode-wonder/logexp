# filename: tests/test_models.py

from datetime import datetime

import pytest
from flask import Flask

from app.config import load_config
from app.models import LogExpReading
from seeds.seed_data import seed_test_data


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
    """
    Ensure to_dict() returns all expected fields, including device_id,
    and that timestamp localization and numeric fields behave correctly.
    """

    reading = LogExpReading(
        id=1,
        timestamp=datetime(2025, 12, 6, 19, 52),  # naive datetime
        counts_per_second=15,
        counts_per_minute=900,
        microsieverts_per_hour=0.05,
        mode="normal",
        device_id="beamrider-0001",
    )

    with app.app_context():
        result = reading.to_dict()

    expected_keys = {
        "id",
        "timestamp",
        "counts_per_second",
        "counts_per_minute",
        "microsieverts_per_hour",
        "mode",
        "device_id",
    }

    # All expected keys present
    assert set(result.keys()) == expected_keys

    # Timestamp localized to America/Chicago
    assert isinstance(result["timestamp"], datetime)
    assert result["timestamp"].tzinfo is not None
    assert result["timestamp"].tzinfo.key == "America/Chicago"

    # Numeric fields match
    assert result["counts_per_second"] == 15
    assert result["counts_per_minute"] == 900
    assert result["microsieverts_per_hour"] == 0.05
    assert result["mode"] == "normal"

    # Device ID preserved
    assert result["device_id"] == "beamrider-0001"


def test_logexp_reading_model(test_app, db_session):
    """
    Ensure seeded test data loads correctly and matches expected values.
    """

    seed_test_data(test_app)  # insert row

    result = db_session.query(LogExpReading).first()

    assert result.counts_per_second == 1
    assert result.counts_per_minute == 60
    assert result.microsieverts_per_hour == 0.01
    assert result.mode == "test"

    # Seed data does not include device_id, so it should be None
    assert result.device_id is None
