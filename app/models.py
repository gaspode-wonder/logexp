# filename: app/models.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast
from zoneinfo import ZoneInfo

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from app.db_types import Base, UTCDateTime
from app.logging_setup import get_logger
from app.typing import LogExpFlask

logger = get_logger("beamfoundry.models")


# ---------------------------------------------------------------------------
# LogExpReading
# ---------------------------------------------------------------------------


class LogExpReading(Base):
    __tablename__ = "logexp_readings"

    id: Mapped[int] = mapped_column(primary_key=True)

    timestamp: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
    )

    counts_per_second: Mapped[int] = mapped_column(nullable=False)
    counts_per_minute: Mapped[int] = mapped_column(nullable=False)
    microsieverts_per_hour: Mapped[float] = mapped_column(nullable=False)
    mode: Mapped[str] = mapped_column(String(10), nullable=False)

    device_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __init__(
        self,
        *,
        counts_per_second: int,
        counts_per_minute: int,
        microsieverts_per_hour: float,
        mode: str,
        timestamp: Optional[datetime] = None,
        id: Optional[int] = None,
        device_id: Optional[str] = None,
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
                "device_id": device_id,
            },
        )

        if id is not None:
            self.id = id

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
        self.device_id = device_id

    def to_dict(self) -> Dict[str, Any]:
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
            "device_id": self.device_id,
        }


Reading = LogExpReading


# ---------------------------------------------------------------------------
# User model — unified under Flask-SQLAlchemy
# ---------------------------------------------------------------------------


class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __init__(self, username: str, password_hash: str) -> None:
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # Flask-Login compatibility attributes
    is_authenticated: bool = True
    is_active: bool = True
    is_anonymous: bool = False

    def get_id(self) -> str:
        return str(self.id)
