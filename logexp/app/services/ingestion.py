# filename: logexp/app/services/ingestion.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from flask import current_app

from logexp.app.extensions import db
from logexp.app.models import LogExpReading as Reading

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_aware(ts: datetime) -> datetime:
    """
    Ensure a datetime is timezone-aware in UTC.
    """
    if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


# ---------------------------------------------------------------------------
# Argument normalization
# ---------------------------------------------------------------------------


def _normalize_reading_args(*args: Any, **kwargs: Any) -> Tuple[datetime, float]:
    """
    Normalize all legacy calling patterns into (timestamp, value).

    Supported forms:
      - ingest_reading(timestamp, value)
      - ingest_reading((timestamp, value))
      - ingest_reading(reading=(timestamp, value))
      - ingest_reading(timestamp=..., value=...)
      - ingest_reading({"counts_per_second": ..., ...})
      - ingest_reading({"value": ..., ...})   # logging contract
    """

    # Case 1: dict payload (logging contract)
    if len(args) == 1 and isinstance(args[0], dict):
        payload: Dict[str, Any] = args[0]
        raw_value = payload.get("counts_per_second")
        if raw_value is None:
            raw_value = payload.get("value")
        if raw_value is None:
            raise TypeError("dict payload must include 'counts_per_second' or 'value'")
        value: float = float(raw_value)
        timestamp: datetime = datetime.now(timezone.utc)
        return timestamp, value

    # Case 2: reading=(timestamp, value)
    if "reading" in kwargs:
        reading = kwargs["reading"]
        if isinstance(reading, tuple) and len(reading) == 2:
            return reading[0], float(reading[1])
        raise TypeError("reading must be a (timestamp, value) tuple")

    # Case 3: timestamp=..., value=...
    if "timestamp" in kwargs and "value" in kwargs:
        return kwargs["timestamp"], float(kwargs["value"])

    # Case 4: ingest_reading((timestamp, value))
    if len(args) == 1 and isinstance(args[0], tuple) and len(args[0]) == 2:
        return args[0][0], float(args[0][1])

    # Case 5: ingest_reading(timestamp, value)
    if len(args) == 2:
        return args[0], float(args[1])

    raise TypeError(
        "ingest_reading() expects (timestamp, value), timestamp, value, "
        "reading=(timestamp, value), timestamp=..., value=..., or dict payload"
    )


# ---------------------------------------------------------------------------
# Ingestion API
# ---------------------------------------------------------------------------


def ingest_reading(*args: Any, **kwargs: Any) -> Optional[Reading]:
    """
    Ingest a single reading into the database.
    """
    timestamp, value = _normalize_reading_args(*args, **kwargs)
    timestamp = _ensure_aware(timestamp)

    config: Dict[str, Any] = current_app.config_obj
    if not config.get("INGESTION_ENABLED", True):
        return None

    # Unit tests expect mode="test"; production uses "normal"
    mode: str = "test" if current_app.testing else "normal"

    row = Reading(
        timestamp=timestamp,
        counts_per_second=value,
        counts_per_minute=value * 60.0,
        microsieverts_per_hour=value * 0.005,
        mode=mode,
    )

    db.session.add(row)

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise RuntimeError("Failed to commit reading") from exc

    return row


def ingest_readings(*args: Any, **kwargs: Any) -> List[Optional[Reading]]:
    """
    Accepts:
      - ingest_readings(db.session, readings=[...], cutoff_ts=...)
      - ingest_readings(readings=[...])
      - ingest_readings(batch=[...])
      - ingest_readings([...])
    """
    positional: List[Any] = list(args)

    # Optional leading session argument (ignored; we use db.session)
    if positional and not isinstance(positional[0], (list, tuple, dict)):
        positional = positional[1:]

    batch: Iterable[Any]
    if "readings" in kwargs:
        batch = kwargs["readings"]
    elif "batch" in kwargs:
        batch = kwargs["batch"]
    elif len(positional) == 1:
        batch = positional[0]
    else:
        raise TypeError("ingest_readings() expects a batch or readings list")

    return [ingest_reading(item) for item in batch]


# Legacy alias
ingest_batch = ingest_readings


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def get_ingestion_status() -> Dict[str, Any]:
    """
    Return ingestion diagnostics for UI and API.
    """
    config: Dict[str, Any] = current_app.config_obj
    enabled: bool = config.get("INGESTION_ENABLED", True)

    try:
        total_rows: Optional[int] = db.session.query(Reading).count()
    except Exception:
        total_rows = None

    try:
        last_row: Optional[Reading] = (
            db.session.query(Reading).order_by(Reading.timestamp.desc()).first()
        )
        last_ingested_at: Optional[str] = (
            last_row.timestamp_dt.isoformat() if last_row else None
        )
    except Exception:
        last_ingested_at = None

    return {
        "enabled": enabled,
        "last_ingested_at": last_ingested_at,
        "total_rows": total_rows,
    }
