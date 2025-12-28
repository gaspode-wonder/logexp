# logexp/app/ingestion.py

from datetime import datetime, timezone

from flask import current_app

from logexp.app.extensions import db
from logexp.app.models import LogExpReading


def ingest_reading(parsed: dict) -> LogExpReading:
    """
    Persist a single parsed reading and return the model instance.

    Respects the INGESTION_ENABLED flag from either config_obj or Flask config.
    """

    # Prefer centralized config_obj, fall back to Flask config
    config_obj = getattr(current_app, "config_obj", {})
    flask_config = current_app.config

    ingestion_enabled = (
        config_obj.get("INGESTION_ENABLED",
        flask_config.get("INGESTION_ENABLED", True))
    )

    if not ingestion_enabled:
        current_app.logger.debug(
            "Ingestion disabled by config; skipping DB write."
        )
        return None

    reading = LogExpReading(
        timestamp=datetime.now().astimezone(timezone.utc),
        counts_per_second=parsed["counts_per_second"],
        counts_per_minute=parsed["counts_per_minute"],
        microsieverts_per_hour=parsed["microsieverts_per_hour"],
        mode=parsed["mode"],
    )

    try:
        session = db.session  # capture the proxy
        session.add(reading)  # underlying session is fine here

        # IMPORTANT: call commit on the PROXY, not the underlying session
        db.session.commit()

    except Exception as exc:
        db.session.rollback()  # rollback must also hit the proxy
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
