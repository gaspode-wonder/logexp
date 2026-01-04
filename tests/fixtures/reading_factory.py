# filename: tests/fixtures/reading_factory.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Tuple, List

import pytest

from logexp.app.extensions import db
from logexp.app.models import LogExpReading
from logexp.analytics.engine import ReadingSample


# ---------------------------------------------------------------------------
# DB-backed factory for integration tests (unit/test_analytics.py, etc.)
# ---------------------------------------------------------------------------


@pytest.fixture
def reading_factory(db_session):
    """
    Returns a factory function that creates LogExpReading rows
    bound to the current test database session.

    Domain rules:
    - cps (counts per second) must be an integer
    - cpm (counts per minute) must be an integer
    - microsieverts_per_hour is a float
    """

    def _create_reading(
        timestamp,
        cps: float | int = 1,
        cpm: float | int | None = None,
        microsieverts_per_hour: float = 0.01,
        mode: str = "test",
    ) -> LogExpReading:
        # Normalize timestamp input
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Derive CPM if not provided
        if cpm is None:
            cpm = cps * 60

        cps_int = int(cps)
        cpm_int = int(cpm)

        reading = LogExpReading(
            timestamp=timestamp,
            counts_per_second=cps_int,
            counts_per_minute=cpm_int,
            microsieverts_per_hour=float(microsieverts_per_hour),
            mode=mode,
        )

        db.session.add(reading)
        return reading

    return _create_reading


# ---------------------------------------------------------------------------
# In-memory factories for pure analytics engine tests (tests/test_analytics.py)
# ---------------------------------------------------------------------------


@pytest.fixture
def make_reading():
    """
    Factory for creating ReadingSample objects used by pure analytics tests.
    """

    def _make_reading(
        timestamp,
        cps: float | int = 1.0,
    ) -> ReadingSample:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return ReadingSample(
            timestamp=timestamp,
            value=float(cps),
        )

    return _make_reading


@pytest.fixture
def make_batch(make_reading):
    """
    Accepts a list of (timestamp, cps) tuples and returns a list of ReadingSample.
    """

    def _batch(items: Iterable[Tuple[datetime, float]]) -> List[ReadingSample]:
        return [make_reading(ts, cps) for ts, cps in items]

    return _batch
