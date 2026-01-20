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
from typing import Union
from zoneinfo import ZoneInfo

from app.logging_setup import get_logger

logger = get_logger("beamfoundry.timestamps")

UTC: ZoneInfo = ZoneInfo("UTC")


def normalize_timestamp(value: Union[str, datetime.datetime]) -> datetime.datetime:
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
    logger.debug(
        "normalize_timestamp_called",
        extra={"type": str(type(value)), "value_preview": str(value)[:50]},
    )

    if isinstance(value, datetime.datetime):
        dt: datetime.datetime = value
        logger.debug("normalize_timestamp_datetime_input")

    elif isinstance(value, str):
        try:
            dt = datetime.datetime.fromisoformat(value)
            logger.debug("normalize_timestamp_string_parsed")
        except Exception as exc:
            logger.error(
                "normalize_timestamp_invalid_string",
                extra={"value": value, "error": str(exc)},
            )
            raise ValueError(f"Invalid timestamp string: {value}") from exc

    else:
        raise TypeError(f"Unsupported timestamp type: {type(value)}")

    if dt.tzinfo is None:
        utc_dt = dt.replace(tzinfo=UTC)
        logger.debug("normalize_timestamp_naive_attached_utc")
        return utc_dt

    utc_dt = dt.astimezone(UTC)
    logger.debug("normalize_timestamp_converted_to_utc")

    return utc_dt
