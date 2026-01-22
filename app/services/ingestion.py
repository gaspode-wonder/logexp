# filename: logexp/app/services/ingestion.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast

from flask import current_app

from ..extensions import db
from ..logging_setup import get_logger
from ..models import LogExpReading
from ..typing import LogExpFlask

logger = get_logger("logexp.ingestion")


def get_config() -> Dict[str, Any]:
    app = cast(LogExpFlask, current_app)
    return app.config_obj


def _normalize_timestamp(raw: Any) -> datetime:
    """
    Convert incoming timestamps into canonical UTC-aware datetime objects.

    Supported formats:
      - float/int epoch seconds
      - ISO8601 strings
      - datetime objects (naive or aware)
      - None → now()
    """
    if raw is None:
        return datetime.now(timezone.utc)

    # float/int epoch seconds
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(raw, tz=timezone.utc)

    # ISO8601 string
    if isinstance(raw, str):
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    # datetime object
    if isinstance(raw, datetime):
        if raw.tzinfo is None:
            return raw.replace(tzinfo=timezone.utc)
        return raw.astimezone(timezone.utc)

    raise TypeError(f"Unsupported timestamp type: {type(raw)}")


def ingest_reading(payload: Dict[str, Any]) -> Optional[LogExpReading]:
    logger.info("ingestion_start")

    config = get_config()
    if not config.get("INGESTION_ENABLED", True):
        logger.info("ingestion_skipped", extra={"reason": "disabled"})
        return None

    logger.info("ingestion_payload_received", extra={"payload": payload})

    try:
        timestamp = _normalize_timestamp(payload.get("timestamp"))

        reading = LogExpReading(
            counts_per_second=payload["counts_per_second"],
            counts_per_minute=payload["counts_per_minute"],
            microsieverts_per_hour=payload["microsieverts_per_hour"],
            mode=payload["mode"],
            timestamp=timestamp,
        )

        db.session.add(reading)
        db.session.commit()

        logger.info("ingestion_complete", extra={"id": reading.id})
        return reading

    except Exception as exc:
        db.session.rollback()
        logger.error("ingestion_error", extra={"error": str(exc)})
        raise


def load_historical_readings(limit: Optional[int] = None) -> Any:
    from ..models import LogExpReading

    query = db.session.query(LogExpReading).order_by(LogExpReading.timestamp.desc())
    if limit:
        query = query.limit(limit)

    logger.debug("historical_readings_loaded", extra={"limit": limit})
    return query.all()


def run_ingestion_diagnostics() -> Dict[str, Any]:
    config = get_config()
    enabled = config.get("INGESTION_ENABLED", True)

    result: Dict[str, Any] = {"enabled": enabled}
    logger.debug("ingestion_diagnostics_complete", extra=result)
    return result


def get_ingestion_status() -> Dict[str, Any]:
    return run_ingestion_diagnostics()
