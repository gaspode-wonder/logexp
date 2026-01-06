# filename: logexp/app/models.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from logexp.app.db_types import UTCDateTime
from logexp.app.extensions import Base
from logexp.app.logging_setup import get_logger
from logexp.app.typing import LogExpFlask

logger = get_logger("logexp.models")


class LogExpReading(Base):
    __tablename__ = "logexp_readings"

    # --- SQLAlchemy 2.0 typed columns ---
    id: Mapped[int] = mapped_column(primary_key=True)

    # Canonical SQLite‑safe UTC datetime type
    timestamp: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
    )

    counts_per_second: Mapped[int] = mapped_column(nullable=False)
    counts_per_minute: Mapped[int] = mapped_column(nullable=False)
    microsieverts_per_hour: Mapped[float] = mapped_column(nullable=False)
    mode: Mapped[str] = mapped_column(String(10), nullable=False)

    # --- Typed initializer ---
    def __init__(
        self,
        *,
        counts_per_second: int,
        counts_per_minute: int,
        microsieverts_per_hour: float,
        mode: str,
        timestamp: Optional[datetime] = None,
        id: Optional[int] = None,
    ) -> None:
        logger.debug(
            "logexp_reading_init",
            extra={
                "cps": counts_per_second,
                "cpm": counts_per_minute,
                "usv": microsieverts_per_hour,
                "mode": mode,
                "timestamp_provided": timestamp is not None,
                "id_provided": id is not None,
            },
        )

        if id is not None:
            self.id = id

        # Canonical UTC-aware timestamp handling
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        elif timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            timestamp = timestamp.astimezone(timezone.utc)

        self.timestamp = timestamp

        self.counts_per_second = counts_per_second
        self.counts_per_minute = counts_per_minute
        self.microsieverts_per_hour = microsieverts_per_hour
        self.mode = mode

    # --- Serialization ---
    def to_dict(self) -> Dict[str, Any]:
        # Explicit cast so mypy knows config_obj exists
        typed_app = cast(LogExpFlask, current_app)

        tz_name = typed_app.config_obj.get("LOCAL_TIMEZONE", "UTC")
        tz = ZoneInfo(tz_name)

        localized_ts = self.timestamp.astimezone(tz) if self.timestamp else None

        logger.debug(
            "logexp_reading_serialize",
            extra={
                "id": self.id,
                "timezone": tz_name,
                "has_timestamp": self.timestamp is not None,
            },
        )

        return {
            "id": self.id,
            "timestamp": localized_ts,
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
        }


# Backward‑compatible alias expected by tests and services
Reading = LogExpReading
