import pytest
from logexp.seeds.seed_data import seed_test_data


def test_health_endpoint(test_app, test_client):
    resp = test_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


def test_readings_endpoint_returns_data(test_client, test_app, db_session):
    # Seed one row
    seed_test_data(test_app)

    response = test_client.get("/api/readings")
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["counts_per_second"] == 1
    assert data[0]["counts_per_minute"] == 60
    assert data[0]["microsieverts_per_hour"] == 0.01
    assert data[0]["mode"] == "test"


def test_readings_endpoint_empty(test_client, db_session):
    # No seeding here → DB should be empty
    response = test_client.get("/api/readings")
    assert response.status_code == 200
    assert response.get_json() == []


def test_diagnostics_page_loads(test_app, test_client):
    resp = test_client.get("/diagnostics")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Diagnostics</h2>" in html
    assert "Poller Status:" in html
