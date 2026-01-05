# filename: logexp/seeds/seed_data.py

from __future__ import annotations

from flask import Flask

from logexp.app.extensions import db
from logexp.app.logging_setup import get_logger
from logexp.app.models import LogExpReading

logger = get_logger("logexp.seeds")


def run(app: Flask) -> None:
    with app.app_context():
        logger.debug("seed_run_start")
        seed_test_data(app)
        logger.debug("seed_run_complete")


def seed_test_data(app: Flask) -> None:
    """
    Insert deterministic test data for development and CI.
    Tests expect exactly one row with specific values.
    """
    with app.app_context():
        logger.debug("seed_test_data_start")

        deleted = db.session.query(LogExpReading).delete()
        logger.debug("seed_deleted_existing_rows", extra={"count": deleted})

        sample = LogExpReading(
            counts_per_second=1,
            counts_per_minute=60,
            microsieverts_per_hour=0.01,
            mode="test",
        )

        db.session.add(sample)
        db.session.commit()

        logger.debug(
            "seed_inserted_sample",
            extra={
                "cps": 1,
                "cpm": 60,
                "usv": 0.01,
                "mode": "test",
            },
        )

        logger.debug("seed_test_data_complete")
