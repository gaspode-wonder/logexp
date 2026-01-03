# filename: logexp/seeds/seed_data.py

from __future__ import annotations

from flask import Flask

from logexp.app.extensions import db
from logexp.app.models import LogExpReading


def run(app: Flask) -> None:
    with app.app_context():
        seed_test_data(app)


def seed_test_data(app: Flask) -> None:
    """
    Insert deterministic test data for development and CI.
    Tests expect exactly one row with specific values.
    """
    with app.app_context():
        db.session.query(LogExpReading).delete()

        sample = LogExpReading(
            counts_per_second=1,
            counts_per_minute=60,
            microsieverts_per_hour=0.01,
            mode="test",
        )

        db.session.add(sample)
        db.session.commit()
