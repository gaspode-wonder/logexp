# filename: logexp/app/services/ingestion.py

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Iterable, List, Mapping, Sequence

from flask import current_app
from sqlalchemy.orm import Session

from logexp.app.extensions import db
from logexp.app.models import LogExpReading
from logexp.validation.ingestion_validator import validate_ingestion_payload

log = logging.getLogger("logexp.ingestion")


def _ingest_core(
    readings: Sequence[Mapping[str, Any]],
    *,
    session: Session,
    validate: bool = True,
) -> List[LogExpReading]:
    """
    Shared ingestion core.

    Responsibilities:
      - log ingestion_start / ingestion_complete
      - optionally validate payloads (graceful skip)
      - normalize timestamps
      - construct LogExpReading models
      - insert into DB with commit/rollback
      - return list[LogExpReading]
    """
    total = len(readings)
    inserted = 0
    skipped = 0

    log.info(
        "ingestion_start",
        extra={"event": "ingestion_start", "total_input_rows": total},
    )

    models: List[LogExpReading] = []

    for raw in readings:
        # ------------------------------------------------------------
        # Step 0: Legacy behavior — inject timestamp if missing
        # ------------------------------------------------------------
        raw = dict(raw)
        if "timestamp" not in raw:
            raw["timestamp"] = datetime.now(timezone.utc)

        # ------------------------------------------------------------
        # Step 1: Validate payload structure (optional)
        # ------------------------------------------------------------
        if validate:
            validated = validate_ingestion_payload(raw)
            if validated is None:
                skipped += 1
                log.info(
                    "ingestion_row_skipped",
                    extra={
                        "event": "ingestion_row_skipped",
                        "reason": "validation_failed",
                        "row": raw,
                    },
                )
                continue
        else:
            validated = raw

        # ------------------------------------------------------------
        # Step 2: Normalize timestamp
        # ------------------------------------------------------------
        try:
            ts = validated["timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)
            validated["timestamp"] = ts
        except Exception as exc:
            skipped += 1
            log.info(
                "ingestion_row_skipped",
                extra={
                    "event": "ingestion_row_skipped",
                    "reason": f"timestamp_error: {exc}",
                    "row": raw,
                },
            )
            continue

        # ------------------------------------------------------------
        # Step 3: Create ORM model instance
        # ------------------------------------------------------------
        try:
            model = LogExpReading(**validated)
            models.append(model)
            inserted += 1
        except Exception as exc:
            skipped += 1
            log.info(
                "ingestion_row_skipped",
                extra={
                    "event": "ingestion_row_skipped",
                    "reason": f"model_error: {exc}",
                    "row": raw,
                },
            )
            continue

    # ------------------------------------------------------------
    # Step 4: Commit or rollback
    # ------------------------------------------------------------
    try:
        for m in models:
            session.add(m)
        session.commit()
    except Exception as exc:
        session.rollback()
        log.error(
            "ingestion_commit_failed",
            extra={
                "event": "ingestion_commit_failed",
                "reason": str(exc),
            },
        )
        raise

    # ------------------------------------------------------------
    # Step 5: Final structured log
    # ------------------------------------------------------------
    log.info(
        "ingestion_complete",
        extra={
            "event": "ingestion_complete",
            "inserted": inserted,
            "skipped": skipped,
        },
    )

    return models


def ingest_readings(
    session,
    *,
    readings,
    cutoff_ts,
):
    """
    Legacy ingestion API preserved for analytics tests.

    Expected call:
        ingest_readings(session, readings=[...], cutoff_ts=...)

    Returns:
        (inserted_count, skipped_count)
    """
    readings_list = list(readings)
    models = _ingest_core(readings_list, session=session, validate=True)

    inserted = len(models)
    skipped = len(readings_list) - inserted

    return inserted, skipped


def ingest_reading(
    reading: Mapping[str, Any],
) -> LogExpReading | None:
    """
    Public single-reading ingestion API.

    Uses validate=False because parsed readings do not match
    the analytics ingestion schema.
    """
    # Respect ingestion-enabled flag (tests mutate config_obj)
    if not current_app.config_obj.get("INGESTION_ENABLED", True):
        return None

    session = db.session
    models = _ingest_core([reading], session=session, validate=False)
    return models[0] if models else None


def ingest_batch(
    readings: Iterable[Mapping[str, Any]],
) -> List[LogExpReading]:
    """
    Public batch ingestion API.
    """
    # Respect ingestion-enabled flag
    if not current_app.config_obj.get("INGESTION_ENABLED", True):
        return []

    session = db.session
    readings_list = list(readings)
    return _ingest_core(readings_list, session=session, validate=True)
