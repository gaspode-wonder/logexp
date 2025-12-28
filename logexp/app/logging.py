import json
import logging
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """
    A deterministic, UTC‑timestamped structured log formatter.

    Produces logs like:
    {"ts": "...", "level": "...", "msg": "...", "name": "..."}
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(payload, separators=(",", ":"))
