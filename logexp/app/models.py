# logexp/app/models.py
from __future__ import annotations

from datetime import datetime, timezone
from .extensions import db
from zoneinfo import ZoneInfo


class LogExpReading(db.Model):
    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    counts_per_second = db.Column(db.Float, nullable=False)
    counts_per_minute = db.Column(db.Float, nullable=False)
    microsieverts_per_hour = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(16), nullable=False)

    def to_dict(self):
        # Localize to America/Chicago for test expectations
        local_tz = ZoneInfo("America/Chicago")

        ts = self.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        localized = ts.astimezone(local_tz)

        return {
            "id": self.id,
            "timestamp": localized,
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }

    @property
    def timestamp_dt(self):
        """
        Return the timestamp as a timezone-aware datetime in UTC.
        Analytics depends on this property.
        """
        ts = self.timestamp
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)
