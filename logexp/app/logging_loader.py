# logexp/app/logging_loader.py

import logging
import json
import sys
from datetime import datetime, timezone
from logging import StreamHandler, Formatter


RESERVED_KEYS = {
    "name", "msg", "args", "levelname", "levelno", "pathname",
    "filename", "module", "exc_info", "exc_text", "stack_info",
    "lineno", "funcName", "created", "msecs", "relativeCreated",
    "thread", "threadName", "processName", "process"
}


class JsonFormatter(Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in RESERVED_KEYS:
                if isinstance(value, datetime):
                    payload[key] = value.isoformat()
                else:
                    payload[key] = value

        return json.dumps(payload)



class DynamicStderrHandler(StreamHandler):
    """
    Writes to the *current* sys.stderr at emit time.
    This is required for pytest's capsys to capture logs.
    """

    def __init__(self):
        super().__init__(stream=None)

    def emit(self, record):
        try:
            self.stream = sys.stderr
            msg = self.format(record)
            self.stream.write(msg + "\n")
            self.stream.flush()
        except Exception:
            self.handleError(record)


def configure_logging(app):
    """
    Strict isolation:
    - Root logger silent
    - Flask/Werkzeug/pytest silent
    - Only logexp.* emits JSON
    - Must run inside app context to override Flask's mutations
    """

    # Silence root
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.CRITICAL + 1)
    root.propagate = False

    # Silence Flask
    app.logger.handlers = []
    app.logger.setLevel(logging.CRITICAL + 1)
    app.logger.propagate = False

    # Silence Werkzeug
    werk = logging.getLogger("werkzeug")
    werk.handlers = []
    werk.setLevel(logging.CRITICAL + 1)
    werk.propagate = False

    # Silence pytest logger
    pytest_logger = logging.getLogger("pytest")
    pytest_logger.handlers = []
    pytest_logger.setLevel(logging.CRITICAL + 1)
    pytest_logger.propagate = False

    # Create JSON handler
    json_handler = DynamicStderrHandler()
    json_formatter = JsonFormatter()
    json_handler.setFormatter(json_formatter)

    # Attach handler to logexp root namespace
    logexp_root = logging.getLogger("logexp")
    logexp_root.handlers = [json_handler]
    logexp_root.setLevel(logging.INFO)
    logexp_root.propagate = True

    # ------------------------------------------------------------------
    # Flask mutates loggers *inside* the app context.
    # We must clean up AFTER those mutations.
    # ------------------------------------------------------------------
    with app.app_context():
        for name in ("logexp.app", "logexp.ingestion", "logexp.analytics"):
            logger = logging.getLogger(name)

            # Remove any handlers Flask attached
            logger.handlers = []

            # Ensure they inherit from logexp root
            logger.setLevel(logging.INFO)
            logger.propagate = True
