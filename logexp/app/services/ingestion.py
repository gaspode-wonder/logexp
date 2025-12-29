# logexp/app/services/ingestion.py

import logging

logger = logging.getLogger("logexp.ingestion")


def ingest_readings(db_session, readings, cutoff_ts):
    """
    Ingest a batch of readings into the database.
    readings: list of dicts
    cutoff_ts: datetime (UTC)
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

    for r in readings:
        try:
            # your existing validation + insert logic
            ...
            inserted += 1
        except Exception as exc:
            skipped += 1
            logger.info(
                "ingestion_row_skipped",
                extra={
                    "event": "ingestion_row_skipped",
                    "reason": str(exc),
                    "row": r,
                },
            )

    db_session.commit()

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
