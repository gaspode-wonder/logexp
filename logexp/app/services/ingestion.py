# filename: logexp/app/ingestion.py
# Step 11C: Schema Enforcement & Validation Integration
#
# This module implements batch ingestion of readings with:
# - payload validation (graceful failure)
# - timestamp normalization
# - structured logging
# - ORM model creation
# - deterministic commit/rollback behavior
from __future__ import annotations

from datetime import datetime
import logging

from logexp.app.models import LogExpReading
from logexp.app.timestamps import normalize_timestamp
from logexp.validation.ingestion_validator import validate_ingestion_payload

logger = logging.getLogger("logexp.ingestion")


def ingest_readings(db_session, readings, cutoff_ts: datetime):
    """
    Ingest a batch of readings into the database.

    readings: list[dict]
    cutoff_ts: datetime (UTC)

    Behavior:
    - Each row is validated via validate_ingestion_payload()
    - Invalid rows are skipped with structured logging
    - Timestamps are normalized to UTC-aware datetimes
    - ORM model instances are created for valid rows
    - Commit is attempted once at the end
    - On commit failure, rollback occurs and the exception is re-raised
    """

    logger.info(
        "ingestion_start",
        extra={
            "event": "ingestion_start",
            "cutoff_ts": cutoff_ts.isoformat(),
            "total_input_rows": len(readings),
        },
    )

    inserted = 0
    skipped = 0

    for raw in readings:
        # ------------------------------------------------------------
        # Step 1: Validate payload structure
        # ------------------------------------------------------------
        validated = validate_ingestion_payload(raw)
        if validated is None:
            skipped += 1
            logger.info(
                "ingestion_row_skipped",
                extra={
                    "event": "ingestion_row_skipped",
                    "reason": "validation_failed",
                    "row": raw,
                },
            )
            continue

        # ------------------------------------------------------------
        # Step 2: Normalize timestamp
        # ------------------------------------------------------------
        try:
            ts = normalize_timestamp(validated["timestamp"])
            validated["timestamp"] = ts
        except Exception as exc:
            skipped += 1
            logger.info(
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
            reading = LogExpReading(**validated)
            db_session.add(reading)
            inserted += 1
        except Exception as exc:
            skipped += 1
            logger.info(
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
        db_session.commit()
    except Exception as exc:
        db_session.rollback()
        logger.error(
            "ingestion_commit_failed",
            extra={
                "event": "ingestion_commit_failed",
                "reason": str(exc),
                "cutoff_ts": cutoff_ts.isoformat(),
            },
        )
        raise

    # ------------------------------------------------------------
    # Step 5: Final structured log
    # ------------------------------------------------------------
    logger.info(
        "ingestion_complete",
        extra={
            "event": "ingestion_complete",
            "inserted": inserted,
            "skipped": skipped,
            "cutoff_ts": cutoff_ts.isoformat(),
        },
    )

    return inserted, skipped
