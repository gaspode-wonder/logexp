# logexp/app/models.py

from __future__ import annotations
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class LogExpReading(db.Model):
    __tablename__ = "logexp_readings"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    counts_per_second = db.Column(db.Float, nullable=False)
    counts_per_minute = db.Column(db.Float, nullable=False)
    microsieverts_per_hour = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(16), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }
