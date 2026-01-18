# filename: logexp/app/db_types.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.types import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """
    Canonical SQLite‑safe timezone‑aware datetime type.
    """

    impl = DateTime()
    cache_ok = True

    def process_bind_param(
        self,
        value: Optional[datetime],
        dialect: Any,
    ) -> Optional[datetime]:
        if value is None:
            return None

        # Normalize to UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        # Return a datetime, NOT a string
        return value

    def process_result_value(
        self,
        value: Optional[datetime],
        dialect: Any,
    ) -> Optional[datetime]:
        if value is None:
            return None

        # SQLite sometimes returns naive datetimes
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)
