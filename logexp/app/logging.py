# filename: logexp/app/logging.py

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from typing import Any


class StructuredFormatter(logging.Formatter):
    """
    A deterministic, UTC‑timestamped structured log formatter.

    Produces logs like:
        {"ts": "...", "level": "...", "msg": "...", "name": "..."}
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }

        # Write JSON to record.message, not record.msg
        record.message = json.dumps(payload)

        return record.message
