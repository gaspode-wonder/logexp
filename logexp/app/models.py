from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from zoneinfo import ZoneInfo

from flask import current_app

from logexp.app.extensions import db


class Reading(db.Model):
    """
    Legacy model used by older ingestion paths.
    Kept abstract so it does not create a table.
    """

    __abstract__ = True
    __allow_unmapped__ = True

    id: int
    cpm: int
    timestamp: datetime


class LogExpReading(db.Model):
    """
    Primary reading model for LogExp.

    Timestamps are stored in SQLite as ISO8601 strings with timezone info.
    """

    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    counts_per_second = db.Column(db.Float, nullable=False, default=1.0)
    counts_per_minute = db.Column(db.Float, nullable=False, default=60.0)
    microsieverts_per_hour = db.Column(db.Float, nullable=False, default=0.01)
    mode = db.Column(db.String(32), nullable=False, default="test")

    @property
    def timestamp_dt(self) -> datetime:
        """
        Return the timestamp as a timezone-aware datetime.

        Handles both:
        - ISO8601 strings (normal case)
        - datetime objects (some tests pass raw datetimes)
        """
        ts = self.timestamp

        if isinstance(ts, datetime):
            # Already a datetime; ensure tz-aware
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return ts

        # Stored as ISO8601 string
        ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize with timestamp localized to LOCAL_TIMEZONE.
        """
        ts = self.timestamp_dt

        config_obj = getattr(current_app, "config_obj", {}) or {}
        local_tz_name = config_obj.get("LOCAL_TIMEZONE", "UTC")
        local_tz = ZoneInfo(local_tz_name)

        ts_local = ts.astimezone(local_tz)

        return {
            "id": self.id,
            "timestamp": ts_local,
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }
