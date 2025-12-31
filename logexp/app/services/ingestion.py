# filename: logexp/app/services/ingestion.py
#
# This module implements batch ingestion of readings with:
# - payload validation (graceful failure)
# - timestamp normalization
# - structured logging
# - ORM model creation
# - deterministic commit/rollback behavior
from __future__ import annotations

from datetime import datetime, timezone
import logging

from logexp.app.models import LogExpReading
from logexp.app.timestamps import normalize_timestamp
from logexp.validation.ingestion_validator import validate_ingestion_payload

log = logging.getLogger("logexp.ingestion")


def ingest_readings(session, *, readings, cutoff_ts):
    """
    Legacy ingestion entry point used by analytics/logging tests.
    """

    log.info("ingestion_start")

    created = []

    for payload in readings:
        validated = validate_ingestion_payload(payload)
        if validated is None:
            continue

        try:
            ts = datetime.fromisoformat(validated["timestamp"])
        except Exception:
            continue

        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)

        reading = LogExpReading(
            timestamp=ts,
            counts_per_second=float(validated["cps"]),
            counts_per_minute=float(validated["cpm"]),
            microsieverts_per_hour=float(validated["usv"]),
            mode=validated["mode"],
        )

        session.add(reading)
        created.append(reading)

    session.commit()

    log.info("ingestion_complete")
    return created


def ingest_batch(session, *, readings):
    """
    Batch ingestion entry point.

    Parameters:
        session: SQLAlchemy session (db.session)
        readings: list of dicts

    Behavior:
        - Logs batch start
        - Validates each reading
        - Normalizes timestamps to UTC
        - Inserts valid readings into DB
        - Skips invalid readings gracefully
        - Logs batch completion
        - Returns list of created LogExpReading instances
    """

    log.info("batch_ingestion_start")

    created = []

    for payload in readings:
        validated = validate_ingestion_payload(payload)
        if validated is None:
            # Skip invalid rows
            continue

        try:
            ts = datetime.fromisoformat(validated["timestamp"])
        except Exception:
            continue

        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)

        reading = LogExpReading(
            timestamp=ts,
            counts_per_second=float(validated["cps"]),
            counts_per_minute=float(validated["cpm"]),
            microsieverts_per_hour=float(validated["usv"]),
            mode=validated["mode"],
        )

        session.add(reading)
        created.append(reading)

    session.commit()

    log.info("batch_ingestion_complete")
    return created
