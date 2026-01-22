# filename: tests/integration/test_ingestion_latest_reading.py

import pytest

from app.models import LogExpReading


@pytest.mark.usefixtures("test_client")
def test_latest_reading_returns_canonical_schema(test_client, db_session):
    """
    Validate that /api/readings/latest returns a ReadingResponse-shaped payload
    when a reading exists in the database. This test exercises LogExp only,
    without relying on any external ingestion sources.
    """

    # Ensure DB is clean
    db_session.query(LogExpReading).delete()
    db_session.commit()

    # Insert a deterministic reading
    reading = LogExpReading(
        counts_per_second=5,
        counts_per_minute=300,
        microsieverts_per_hour=0.05,
        mode="normal",
        device_id="test-device",
    )
    db_session.add(reading)
    db_session.commit()

    # Hit the endpoint
    resp = test_client.get("/api/readings/latest")
    assert resp.status_code == 200

    data = resp.get_json()

    expected_keys = {
        "id",
        "timestamp",
        "counts_per_second",
        "counts_per_minute",
        "microsieverts_per_hour",
        "mode",
        "device_id",
    }

    assert set(data.keys()) == expected_keys

    # Validate types
    assert isinstance(data["id"], int)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["counts_per_second"], int)
    assert isinstance(data["counts_per_minute"], int)
    assert isinstance(data["microsieverts_per_hour"], float)
    assert isinstance(data["mode"], str)
    assert data["device_id"] == "test-device"
