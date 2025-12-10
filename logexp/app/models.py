from datetime import datetime, timezone
import pytz
from flask import current_app
from logexp.app.extensions import db

class LogExpReading(db.Model):
    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)
    # Store timestamps in UTC by default
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    counts_per_second = db.Column(db.Integer, nullable=False)
    counts_per_minute = db.Column(db.Integer, nullable=False)
    microsieverts_per_hour = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(32), nullable=False)

    def to_dict(self):
        """
        Convert the reading into a dictionary suitable for Pydantic validation.
        Returns a timezone-aware datetime object for 'timestamp'.
        """
        # Ensure timestamp is treated as UTC
        utc = pytz.utc
        ts_utc = self.timestamp
        if ts_utc.tzinfo is None:
            ts_utc = utc.localize(ts_utc)

        # Convert to local timezone configured in Flask
        local_tz = pytz.timezone(current_app.config["LOCAL_TIMEZONE"])
        ts_local = ts_utc.astimezone(local_tz)

        return {
            "id": self.id,
            "timestamp": ts_local,  # datetime object, not string
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }
