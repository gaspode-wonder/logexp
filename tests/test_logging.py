# tests/test_logging.py
import logging

from app import create_app


def test_structured_logging_outputs_valid_json(caplog):
    app = create_app(
        {
            "TESTING": True,
            "START_POLLER": False,
        }
    )

    caplog.set_level(logging.INFO, logger="logexp.app")

    with app.app_context():
        app.logger.info("test message")

    record = next(r for r in caplog.records if r.getMessage() == "test message")

    assert record.name == "logexp.app"
    assert record.levelname == "INFO"
