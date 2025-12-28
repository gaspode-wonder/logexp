# logexp/app/ingestion.py

from datetime import datetime, timezone

from flask import current_app

from logexp.app.extensions import db
from logexp.app.models import LogExpReading


def ingest_reading(parsed: dict) -> LogExpReading:
    """
    Persist a single parsed reading and return the model instance.

    Respects the INGESTION_ENABLED flag in the centralized config.
    """
    config = current_app.config

    if not config["INGESTION_ENABLED"]:
        current_app.logger.debug(
            "Ingestion disabled by config (INGESTION_ENABLED=False); skipping DB write."
        )
        return None  # explicit: nothing was written

    reading = LogExpReading(
        timestamp=datetime.now().astimezone(timezone.utc),
        counts_per_second=parsed["counts_per_second"],
        counts_per_minute=parsed["counts_per_minute"],
        microsieverts_per_hour=parsed["microsieverts_per_hour"],
        mode=parsed["mode"],
    )

    try:
        db.session.add(reading)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("Ingestion error: %s", exc)
        raise RuntimeError("Failed to ingest reading") from exc

    current_app.logger.debug(
        "Ingested reading id=%s cps=%s cpm=%s µSv/h=%s mode=%s",
        reading.id,
        reading.counts_per_second,
        reading.counts_per_minute,
        reading.microsieverts_per_hour,
        reading.mode,
    )

    return reading
