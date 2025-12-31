# filename: logexp/app/timestamps.py
"""
Canonical timestamp normalization utilities for LogExp.

This module provides a single, well-defined normalization function used by
ingestion, analytics, and any future data pipelines.

Contract:
- Accepts strings or datetime objects
- Parses ISO8601 strings into datetime objects
- Ensures all timestamps are timezone-aware
- Naive timestamps are assumed to be UTC
- Returns UTC-aware datetime objects
"""

from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo

UTC = ZoneInfo("UTC")


def normalize_timestamp(value) -> datetime.datetime:
    """
    Normalize a timestamp into a UTC-aware datetime.

    Accepts:
    - ISO8601 strings
    - datetime.datetime objects (naive or aware)

    Returns:
    - datetime.datetime (UTC-aware)

    Raises:
    - ValueError for invalid formats
    - TypeError for unsupported types
    """

    # Already a datetime
    if isinstance(value, datetime.datetime):
        dt = value
    # Parse ISO8601 string
    elif isinstance(value, str):
        try:
            dt = datetime.datetime.fromisoformat(value)
        except Exception as exc:
            raise ValueError(f"Invalid timestamp string: {value}") from exc
    else:
        raise TypeError(f"Unsupported timestamp type: {type(value)}")

    # Attach UTC if naive
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)

    # Convert aware timestamps to UTC
    return dt.astimezone(UTC)
