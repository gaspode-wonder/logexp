# tests/test_logging.py
"""
Tests for structured logging JSON format.
"""

import json
import logging


def test_structured_logging_outputs_valid_json(test_app, capsys):
    with test_app.app_context():
        logger = logging.getLogger("logexp.app")
        logger.info("test message", extra={"foo": "bar"})

    captured = capsys.readouterr()
    text = (captured.err or "") + (captured.out or "")
    lines = [l for l in text.splitlines() if l.strip()]
    assert lines, "No log lines captured"

    payload = json.loads(lines[-1])

    assert payload["message"] == "test message"
    assert payload["foo"] == "bar"
    assert "level" in payload
    assert "timestamp" in payload
