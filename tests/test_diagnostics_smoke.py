# FILE: tests/test_diagnostics_smoke.py
import json


def test_diagnostics_endpoint_available(test_client):
    resp = test_client.get("/api/diagnostics")
    assert resp.status_code == 200


def test_diagnostics_payload_shape(test_client):
    payload = test_client.get("/api/diagnostics").get_json()
    for key in ["config", "ingestion", "poller", "analytics", "database", "meta"]:
        assert key in payload


def test_diagnostics_json_safe(test_client):
    payload = test_client.get("/api/diagnostics").get_json()
    json.dumps(payload)  # must not raise


def test_analytics_section_valid(test_client):
    analytics = test_client.get("/api/diagnostics").get_json()["analytics"]
    assert isinstance(analytics["window_minutes"], int)
    assert isinstance(analytics["count"], int)
    assert isinstance(analytics["window_start"], str)
    assert isinstance(analytics["window_end"], str)


def test_database_section_valid(test_client):
    dbs = test_client.get("/api/diagnostics").get_json()["database"]
    assert "uri" in dbs
    assert "engine" in dbs
    assert isinstance(dbs["connected"], bool)
    assert "schema_ok" in dbs


def test_diagnostics_deterministic_under_fixed_time(test_client, freezer):
    freezer.move_to("2024-01-01T12:00:00Z")
    p1 = test_client.get("/api/diagnostics").get_json()
    p2 = test_client.get("/api/diagnostics").get_json()
    assert p1["analytics"]["count"] == p2["analytics"]["count"]
