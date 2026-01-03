# filename: logexp/seeds/seed_data.py

from __future__ import annotations

from typing import Any
from flask import Flask

from logexp.app import db
from logexp.app.models import LogExpReading


def run(app: Flask) -> None:
    """
    Seed the database with initial data.
    """
    with app.app_context():
        seed_test_data(app)


def seed_test_data(app: Flask) -> None:
    """
    Insert deterministic test data for development and CI.
    """
    with app.app_context():
        db.session.query(LogExpReading).delete()

        samples = [
            LogExpReading(
                counts_per_second=10,
                counts_per_minute=600,
                microsieverts_per_hour=0.12,
                mode="FAST",
            ),
            LogExpReading(
                counts_per_second=5,
                counts_per_minute=300,
                microsieverts_per_hour=0.06,
                mode="SLOW",
            ),
        ]

        for sample in samples:
            db.session.add(sample)

        db.session.commit()
