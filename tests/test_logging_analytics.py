# tests/test_logging_analytics.py

import json
import logging
import sys

from logexp.app.analytics import run_analytics
from logexp.app.extensions import db


def test_analytics_logging_contract(analytics_app, frozen_now, reading_factory, capsys, db_session):
    """
    Ensure analytics results can be logged in structured JSON form.

    This test asserts the logging *contract*:
    - The analytics summary dict can be attached as `extra=...`
    - The log line is emitted as valid JSON
    - The expected analytics fields are present and correctly computed
    """
    logger = analytics_app.logger
    now = frozen_now

    # Seed a few readings
    reading_factory(now, cps=10)
    reading_factory(now, cps=20)
    db.session.commit()

    with analytics_app.app_context():

        result = run_analytics(now=now)
        print(">>> RESULT:", result)

        logger.info("analytics_window", extra=result)

    captured = capsys.readouterr()
    text = (captured.err or "") + (captured.out or "")
    lines = [l for l in text.splitlines() if l.strip()]

    json_lines = []
    for line in lines:
        if line.startswith("{"):
            try:
                json.loads(line)
                json_lines.append(line)
            except Exception:
                pass

    assert json_lines, "No JSON log lines captured"

    payload = json.loads(json_lines[-1])

    assert "timestamp" in payload
    assert "level" in payload
    assert "logger" in payload
    assert "message" in payload
    assert payload["message"] == "analytics_window"

    assert payload["count"] == 2
    assert payload["avg_cps"] == 15
    assert payload["first_timestamp"].endswith("+00:00")
    assert payload["last_timestamp"].endswith("+00:00")
