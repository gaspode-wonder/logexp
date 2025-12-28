import json
import logging
from logexp.app import create_app
from logexp.app.config import TestConfig
from logexp.app.logging import StructuredFormatter


def test_structured_logging_outputs_valid_json(caplog):
    app = create_app(TestConfig)

    # Tell caplog to capture logs from the app logger
    caplog.set_level(logging.INFO, logger="logexp.app")

    with app.app_context():
        app.logger.info("test message")

    # Now caplog WILL contain the record
    record = next(r for r in caplog.records if r.getMessage() == "test message")

    # Apply formatter manually
    formatter = StructuredFormatter()
    formatted = formatter.format(record)
    payload = json.loads(formatted)

    # Required fields
    assert "ts" in payload
    assert "level" in payload
    assert "name" in payload
    assert "msg" in payload

    assert payload["msg"] == "test message"
    assert payload["ts"].endswith("+00:00")
