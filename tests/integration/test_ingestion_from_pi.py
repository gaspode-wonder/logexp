# filename: tests/integration/test_ingestion_from_pi.py

import time

import requests

LOGEXP_BASE = "http://beamrider-0002.local:8000"


def test_pi_log_ingestion():
    """
    Confirm that Pi-log successfully pushes a reading into LogExp
    and that the latest-reading endpoint returns the canonical
    model schema (ReadingResponse).
    """

    # Allow time for Pi-log to push at least one reading
    time.sleep(6)

    # Query LogExp for the most recent reading
    resp = requests.get(f"{LOGEXP_BASE}/api/readings/latest")
    assert resp.status_code == 200

    data = resp.json()

    # Canonical model schema fields
    expected_keys = {
        "id",
        "timestamp",
        "counts_per_second",
        "counts_per_minute",
        "microsieverts_per_hour",
        "mode",
        "device_id",
    }

    # Validate schema
    assert set(data.keys()) == expected_keys

    # Validate timestamp is an ISO string
    assert isinstance(data["timestamp"], str)
    assert "T" in data["timestamp"]

    # Validate numeric fields
    assert isinstance(data["counts_per_second"], int)
    assert isinstance(data["counts_per_minute"], int)
    assert isinstance(data["microsieverts_per_hour"], float)

    # Validate mode
    assert isinstance(data["mode"], str)

    # Confirm the reading originated from Pi-log
    assert data["device_id"] == "pi-log"
