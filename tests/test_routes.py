def test_health_endpoint(test_app, test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"

def test_readings_endpoint_returns_data(test_app, test_client, db_session):
    from datetime import datetime, timezone
    from logexp.app.models import LogExpReading

    reading = LogExpReading(
        timestamp=datetime.now(timezone.utc),
        counts_per_second=42,
        counts_per_minute=2520,
        microsieverts_per_hour=0.15,
        mode="SLOW",
    )
    db_session.add(reading)
    db_session.commit()

    resp = test_client.get("/readings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["counts_per_second"] == 42

def test_readings_endpoint_empty(test_app, test_client):
    resp = test_client.get("/readings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []

def test_diagnostics_page_loads(test_app, test_client):
    resp = test_client.get("/diagnostics")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Diagnostics</h2>" in html
    assert "Poller Status:" in html
