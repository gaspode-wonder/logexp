# filename: tests/test_logging_analytics.py

import logging
from datetime import datetime, timezone

from app.ingestion import ingest_readings
from app.services.analytics import run_analytics


def test_ingestion_logging_contract(caplog, test_app):
    """
    Validate that ingestion emits the correct structured log messages.
    """
    caplog.set_level(logging.INFO)

    with test_app.app_context():
        ingest_readings(
            test_app.extensions["sqlalchemy"].db.session,
            readings=[{"value": 1}],
            cutoff_ts=datetime.now(timezone.utc),
        )

    messages = [r.getMessage() for r in caplog.records]

    assert "ingestion_start" in messages
    assert "ingestion_complete" in messages

    names = {r.name for r in caplog.records}
    assert "logexp.ingestion" in names


def test_analytics_logging_contract(caplog, test_app):
    """
    Validate that analytics emits the correct structured log messages.
    """
    caplog.set_level(logging.INFO)

    with test_app.app_context():
        run_analytics(test_app.extensions["sqlalchemy"].db.session)

    messages = [r.getMessage() for r in caplog.records]

    assert "analytics_start" in messages
    assert "analytics_complete" in messages

    names = {r.name for r in caplog.records}
    assert "logexp.analytics" in names
