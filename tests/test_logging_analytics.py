# tests/test_logging_analytics.py
"""
Tests for analytics-related logging contracts.
"""

import json
import logging

from logexp.app.analytics import run_analytics
from logexp.app.extensions import db


def test_ingestion_logging_contract(test_app, capsys):
    """
    Ensure ingestion actions emit structured logs with required fields.
    """
    with test_app.app_context():
        logger = logging.getLogger("logexp.ingestion")
        logger.info("ingested_reading", extra={"source": "geiger", "status": "ok"})

    captured = capsys.readouterr()
    text = (captured.err or "") + (captured.out or "")
    lines = [l for l in text.splitlines() if l.strip()]
    assert lines, "No log lines captured"

    payload = json.loads(lines[-1])

    assert payload["message"] == "ingested_reading"
    assert payload["source"] == "geiger"
    assert payload["status"] == "ok"


def test_analytics_logging_contract(analytics_app, frozen_now, reading_factory, capsys, db_session):
    """
    Ensure analytics results can be logged in structured form.
    """
    logger = logging.getLogger("logexp.analytics")
    now = frozen_now

    # Seed a few readings
    reading_factory(now, cps=10)
    reading_factory(now, cps=20)
    db.session.commit()

    with analytics_app.app_context():
        result = run_analytics(now=now)
        logger.info("analytics_window", extra=result)

    captured = capsys.readouterr()
    text = (captured.err or "") + (captured.out or "")
    lines = [l for l in text.splitlines() if l.strip()]
    assert lines, "No log lines captured"

    payload = json.loads(lines[-1])

    assert payload["message"] == "analytics_window"
    assert payload["count"] == result["count"]
    assert "avg_cps" in payload
    assert "first_timestamp" in payload
    assert "last_timestamp" in payload
