# filename: logexp/app/ingestion.py
"""
Legacy ingestion wrapper providing the logging contract expected by tests.

The real ingestion logic lives in:
    logexp.app.services.ingestion

This wrapper preserves the legacy API shape:
    - leading session argument
    - readings=[...]
    - cutoff_ts=...
    - structured logging ("ingestion_start", "ingestion_complete")
    - logger name: logexp.ingestion
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Iterable, List, Optional

from logexp.app.services.ingestion import ingest_reading as _ingest_reading

logger: logging.Logger = logging.getLogger("logexp.ingestion")


def ingest_reading(*args: Any, **kwargs: Any) -> Any:
    """
    Legacy single‑row ingestion wrapper.
    """
    logger.info("ingestion_start")
    try:
        row: Any = _ingest_reading(*args, **kwargs)
        logger.info("ingestion_complete")
        return row
    except Exception:
        logger.exception("ingestion_failed")
        raise


def ingest_readings(*args: Any, **kwargs: Any) -> List[Optional[Any]]:
    """
    Legacy wrapper for batch ingestion.

    Accepts:
        ingest_readings(session, readings=[...], cutoff_ts=...)

    Behavior:
    - Leading session argument is ignored.
    - cutoff_ts is accepted but unused (legacy contract).
    - Structured logging is preserved.
    """
    logger.info("ingestion_start")

    positional: List[Any] = list(args)

    # Ignore leading session argument
    if positional and not isinstance(positional[0], (list, tuple, dict)):
        positional = positional[1:]

    readings: Optional[Iterable[Any]] = kwargs.get("readings")
    if readings is None and positional:
        readings = positional[0]

    # cutoff_ts is accepted but unused
    _ = kwargs.get("cutoff_ts", datetime.now(timezone.utc))

    # Guard: never iterate over None
    if readings is None:
        logger.info("ingestion_complete")
        return []

    try:
        results: List[Optional[Any]] = [_ingest_reading(item) for item in readings]
        logger.info("ingestion_complete")
        return results
    except Exception:
        logger.exception("ingestion_failed")
        raise


# Legacy alias
ingest_batch = ingest_readings
