# tests/fixtures/reading_factory.py

import datetime
from logexp.app.models import LogExpReading
from logexp.app.extensions import db


def create_reading(timestamp, cps=10):
    """
    Create a LogExpReading with an explicit timestamp and CPS value.
    Does not commit — caller controls commit boundaries.
    """
    r = LogExpReading(
        timestamp=timestamp,
        counts_per_second=cps,
    )
    db.session.add(r)
    return r
