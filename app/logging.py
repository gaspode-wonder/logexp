# filename: logexp/app/logging.py

from __future__ import annotations

import json
import logging as pylogging
from datetime import datetime, timezone

from .typing import Any

logger = pylogging.getLogger("beamfoundry.logging")


class StructuredFormatter(pylogging.Formatter):
    """
    A deterministic, UTC‑timestamped structured log formatter.

    Produces logs like:
        {"ts": "...", "level": "...", "msg": "...", "name": "..."}
    """

    def __init__(self) -> None:
        super().__init__()
        logger.debug("structured_formatter_initialized")

    def format(self, record: pylogging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }

        record.message = json.dumps(payload)
        return record.message
