# tests/test_routes.py
"""
Route tests for health, readings API, and diagnostics page.
"""

from datetime import datetime, timezone

from logexp.app.models import LogExpReading
from logexp.app.extensions import db


def test_health_endpoint(test_app, test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("status") == "ok"


def test_readings_endpoint_returns_data(test_app, test_client, db_session):
    with test_app.app_context():
        r = LogExpReading(
            timestamp=datetime.now(timezone.utc).isoformat(),
            counts_per_second=1.0,
            counts_per_minute=60.0,
            microsieverts_per_hour=0.01,
            mode="test",
        )
        db.session.add(r)
        db.session.commit()

    resp = test_client.get("/api/readings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["counts_per_second"] == 1.0


def test_readings_endpoint_empty(test_app, test_client, db_session):
    resp = test_client.get("/api/readings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []


def test_diagnostics_page_loads(test_app, test_client):
    resp = test_client.get("/diagnostics")
    assert resp.status_code == 200
    assert b"Diagnostics" in resp.data
