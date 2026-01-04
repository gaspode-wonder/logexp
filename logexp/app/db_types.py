# filename: logexp/app/db_types.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.types import String, TypeDecorator


class UTCDateTime(TypeDecorator):
    """
    Canonical SQLite‑safe timezone‑aware datetime type.

    Stores datetimes as ISO8601 strings with timezone.
    Always returns timezone‑aware UTC datetime objects.
    Works consistently across SQLite, Postgres, MySQL.
    """

    impl = String
    cache_ok = True  # SQLAlchemy 2.0 requirement

    # ------------------------------------------------------------
    # Bind: Python → DB
    # ------------------------------------------------------------
    def process_bind_param(
        self,
        value: Optional[datetime],
        dialect: Any,
    ) -> Optional[str]:
        if value is None:
            return None

        # Normalize to UTC and ensure tz-aware
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        # Store as ISO8601 string with timezone
        return value.isoformat()

    # ------------------------------------------------------------
    # Result: DB → Python
    # ------------------------------------------------------------
    def process_result_value(
        self,
        value: Optional[str],
        dialect: Any,
    ) -> Optional[datetime]:
        if value is None:
            return None

        # Parse ISO8601 string back to aware datetime
        dt = datetime.fromisoformat(value)

        # Ensure tz-aware (SQLite sometimes drops it)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt
