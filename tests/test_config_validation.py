# filename: tests/test_config_validation.py
from logexp.validation.config_validator import validate_config

import pytest


def test_invalid_window():
    with pytest.raises(ValueError):
        validate_config(
            {"ANALYTICS_WINDOW": -1, "LOCAL_TIMEZONE": "UTC", "INGESTION_ENABLED": True}
        )


def test_invalid_timezone():
    with pytest.raises(ValueError):
        validate_config(
            {
                "ANALYTICS_WINDOW": 10,
                "LOCAL_TIMEZONE": "NOPE",
                "INGESTION_ENABLED": True,
            }
        )


def test_valid_config():
    cfg = {"ANALYTICS_WINDOW": 10, "LOCAL_TIMEZONE": "UTC", "INGESTION_ENABLED": True}
    assert validate_config(cfg) == cfg
