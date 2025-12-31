# tests/fixtures/reading_factory.py
from datetime import datetime, timezone

from logexp.app.extensions import db
from logexp.app.models import LogExpReading

import pytest


@pytest.fixture
def reading_factory(db_session):
    """
    Returns a factory function that creates LogExpReading rows
    bound to the current test database session.
    """

    def _create_reading(
        timestamp,
        cps: float = 1.0,
        cpm=None,
        microsieverts_per_hour: float = 0.01,
        mode: str = "test",
    ):
        # Normalize timestamp input
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Derive CPM if not provided
        if cpm is None:
            cpm = cps * 60.0

        reading = LogExpReading(
            timestamp=timestamp,
            counts_per_second=cps,
            counts_per_minute=cpm,
            microsieverts_per_hour=microsieverts_per_hour,
            mode=mode,
        )

        db.session.add(reading)
        return reading

    return _create_reading
