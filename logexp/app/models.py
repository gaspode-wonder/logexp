from datetime import datetime, timezone
from logexp.app.extensions import db

class LogExpReading(db.Model):
    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now().astimezone(timezone.utc),
        nullable=False
    )
    counts_per_second = db.Column(db.Integer, nullable=False)
    counts_per_minute = db.Column(db.Integer, nullable=False)
    microsieverts_per_hour = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(32), nullable=False)

    def to_dict(self):
        ts_utc = self.timestamp.astimezone(timezone.utc)

        return {
            "id": self.id,
            "timestamp": ts_utc.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }




