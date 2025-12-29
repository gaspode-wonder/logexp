# logexp/app/ingestion.py
import datetime

from flask import current_app

from logexp.app.extensions import db
from logexp.app.models import LogExpReading


def ingest_reading(parsed: dict) -> LogExpReading:
    """
    Persist a single parsed reading and return the model instance.

    Respects the INGESTION_ENABLED flag from config_obj.
    """

    config_obj = getattr(current_app, "config_obj", {})
    print("CONFIG_OBJ AT APP START:", current_app.config_obj)

    ingestion_enabled = config_obj.get("INGESTION_ENABLED", True)

    print(
        "INGESTION_ENABLED:",
        ingestion_enabled,
        "called from:",
        __import__("inspect").stack()[1].filename,
    )

    if not ingestion_enabled:
        current_app.logger.debug(
            "Ingestion disabled by config; skipping DB write."
        )
        return None

    reading = LogExpReading(
        timestamp=datetime.datetime.now(datetime.timezone.utc),
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
