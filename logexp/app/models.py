from datetime import datetime, timezone
import pytz
from flask import current_app
from logexp.app.extensions import db

class LogExpReading(db.Model):
    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    counts_per_second = db.Column(db.Integer, nullable=False)
    counts_per_minute = db.Column(db.Integer, nullable=False)
    microsieverts_per_hour = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(32), nullable=False)

    def to_dict(self):
        utc = pytz.utc
        ts_utc = utc.localize(self.timestamp)

        local_tz = pytz.timezone(current_app.config["LOCAL_TIMEZONE"])
        ts_local = ts_utc.astimezone(local_tz)

        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }
