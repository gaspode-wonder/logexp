# tests/test_container_boot.py

import os

from logexp.app import create_app


def test_create_app_smoke() -> None:
    """
    Ensure create_app() can construct a Flask app with canonical env values.
    This mimics the container environment but runs in-process for quick feedback.
    """
    os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
    os.environ.setdefault("LOCAL_TIMEZONE", "UTC")
    os.environ.setdefault("GEIGER_THRESHOLD", "0.1")
    os.environ.setdefault("START_POLLER", "False")
    os.environ.setdefault("LOGEXP_NODE_ID", "test-node")
    os.environ.setdefault("TELEMETRY_ENABLED", "True")
    os.environ.setdefault("TELEMETRY_INTERVAL_SECONDS", "30")

    app = create_app()
    assert app is not None

    with app.app_context():
        client = app.test_client()
        resp = client.get("/api/health")
        assert resp.status_code == 200
