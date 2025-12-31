# logexp/app/logging.py
import json
import logging
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """
    A deterministic, UTC‑timestamped structured log formatter.

    Produces logs like:
    {"ts": "...", "level": "...", "msg": "...", "name": "..."}
    """

    def format(self, record):
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }

        # Write JSON to record.message, not record.msg
        record.message = json.dumps(payload)

        return record.message
