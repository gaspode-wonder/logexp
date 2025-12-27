from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from logexp.app.extensions import db


CENTRAL = ZoneInfo("America/Chicago")


class Reading(db.Model):
    """
    Legacy model used by older ingestion paths.
    """
    id: int
    cpm: int
    timestamp: datetime


class LogExpReading(db.Model):
    """
    Primary reading model for LogExp.

    Stores raw radiation readings and ensures timestamps are always
    timezone-aware and normalized to US/Central when serialized.
    """

    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now().astimezone(timezone.utc),
        nullable=False,
    )
    counts_per_second = db.Column(db.Integer, nullable=False)
    counts_per_minute = db.Column(db.Integer, nullable=False)
    microsieverts_per_hour = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(32), nullable=False)

    def to_dict(self) -> dict:
        """
        Return a pure-Python representation of this reading.

        Ensures timestamp is always timezone-aware and localized to US/Central,
        even if the underlying model instance was constructed with a naive datetime.
        """
        ts = self.timestamp

        # If timestamp is naive, assume it's UTC (safe default)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        # Convert to US/Central for internal consistency
        ts_central = ts.astimezone(CENTRAL)

        return {
            "id": self.id,
            "timestamp": ts_central,
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }