# tests/test_logging_analytics.py
import logging
from datetime import datetime, timezone

from logexp.app import create_app
from logexp.app.extensions import db
from logexp.app.services.ingestion import ingest_readings
from logexp.app.services.analytics import run_analytics


def test_ingestion_logging_contract(caplog):
    app = create_app({
        "TESTING": True,
        "START_POLLER": False,
    })

    caplog.set_level(logging.INFO)

    with app.app_context():
        ingest_readings(
            db.session,
            readings=[{"value": 1}],
            cutoff_ts=datetime.now(timezone.utc),
        )

    messages = [r.getMessage() for r in caplog.records]

    assert "ingestion_start" in messages
    assert "ingestion_complete" in messages

    names = {r.name for r in caplog.records}
    assert "logexp.ingestion" in names


def test_analytics_logging_contract(caplog):
    app = create_app({
        "TESTING": True,
        "START_POLLER": False,
    })

    caplog.set_level(logging.INFO)

    with app.app_context():
        run_analytics(db.session)

    messages = [r.getMessage() for r in caplog.records]

    assert "analytics_start" in messages
    assert "analytics_complete" in messages

    names = {r.name for r in caplog.records}
    assert "logexp.analytics" in names
