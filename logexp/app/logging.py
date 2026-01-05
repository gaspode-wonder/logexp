# filename: logexp/app/logging.py

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("logexp.logging")


class StructuredFormatter(logging.Formatter):
    """
    A deterministic, UTC‑timestamped structured log formatter.

    Produces logs like:
        {"ts": "...", "level": "...", "msg": "...", "name": "..."}
    """

    def __init__(self) -> None:
        super().__init__()
        logger.debug("structured_formatter_initialized")

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }

        record.message = json.dumps(payload)
        return record.message
