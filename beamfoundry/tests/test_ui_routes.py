from tests.helpers.auth import authenticate


# -----------------------------
# UI: /readings
# -----------------------------
def test_readings_page_loads(client):
    authenticate(client)
    resp = client.get("/readings")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Readings</h2>" in html


# -----------------------------
# UI: /diagnostics
# -----------------------------
def test_diagnostics_page_loads(client):
    authenticate(client)
    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Diagnostics</h2>" in html
    assert "Poller Status" in html


# -----------------------------
# UI: /settings
# -----------------------------
def test_settings_page_loads(client):
    authenticate(client)
    resp = client.get("/settings")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Settings</h2>" in html


# -----------------------------
# UI: /analytics
# -----------------------------
def test_analytics_page_loads(client):
    authenticate(client)
    resp = client.get("/analytics")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Analytics</h2>" in html


# -----------------------------
# UI: /docs
# -----------------------------
def test_docs_page_loads(client):
    authenticate(client)
    resp = client.get("/docs")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>Documentation</h2>" in html


# -----------------------------
# UI: /about
# -----------------------------
def test_about_page_loads(client):
    authenticate(client)
    resp = client.get("/about")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "<h2>About</h2>" in html
