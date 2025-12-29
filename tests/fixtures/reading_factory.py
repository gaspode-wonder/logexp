from __future__ import annotations

from datetime import datetime
from typing import Optional

from logexp.app.extensions import db
from logexp.app.models import LogExpReading


def create_reading(
    timestamp,
    cps: float = 1.0,
    cpm: Optional[float] = None,
    microsieverts_per_hour: float = 0.01,
    mode: str = "test",
) -> LogExpReading:
    """
    Test helper to create a LogExpReading and add it to the current session.

    - Accepts timestamp as a datetime or ISO8601 string.
    - Stores timestamp as a timezone-aware datetime in the database.
    """

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
