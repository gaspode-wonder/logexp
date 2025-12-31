# filename: tests/test_ingestion_validation.py

from logexp.validation.ingestion_validator import validate_ingestion_payload


def test_null_field_rejected():
    payload = {
        "cps": 10,
        "cpm": None,
        "usv": 0.1,
        "mode": "SLOW",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    assert validate_ingestion_payload(payload) is None


def test_invalid_mode_rejected():
    payload = {
        "cps": 10,
        "cpm": 20,
        "usv": 0.1,
        "mode": "BAD",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    assert validate_ingestion_payload(payload) is None


def test_valid_payload_passes():
    payload = {
        "cps": 10,
        "cpm": 20,
        "usv": 0.1,
        "mode": "SLOW",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    assert validate_ingestion_payload(payload) is not None
