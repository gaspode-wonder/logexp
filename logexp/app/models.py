# logexp/app/models.py
"""
Database models for LogExp.

This module defines the primary radiation reading model used across
ingestion, analytics, and API serialization. Timestamps are stored as
ISO8601 strings for SQLite portability and parsed into timezone-aware
datetime objects on access.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from flask import current_app
from zoneinfo import ZoneInfo

from logexp.app.extensions import db


class Reading(db.Model):
    """
    Legacy abstract base model used by older ingestion paths.
    Not mapped to a table.
    """

    __abstract__ = True
    __allow_unmapped__ = True

    id: int
    cpm: int
    timestamp: datetime


class LogExpReading(db.Model):
    """
    Primary radiation reading model.

    Timestamps are stored as ISO8601 strings (UTC) for maximum SQLite
    compatibility. The timestamp_dt property returns a timezone-aware
    datetime object for analytics and serialization.
    """

    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)

    # Stored as ISO8601 string (UTC)
    timestamp = db.Column(
        db.String,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
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
            return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

        # Stored as ISO8601 string
        ts = datetime.fromisoformat(ts)
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the reading with timestamp localized to LOCAL_TIMEZONE.
        """
        ts = self.timestamp_dt

        config_obj = getattr(current_app, "config_obj", {}) or {}
        local_tz_name = config_obj.get("LOCAL_TIMEZONE", "UTC")
        local_tz = ZoneInfo(local_tz_name)

        return {
            "id": self.id,
            "timestamp": ts.astimezone(local_tz),
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }
