# filename: logexp/app/services/analytics_readings.py
"""
Analytics reading utilities: load readings, convert to samples, and compute
summary statistics over a window. This module is intentionally pure and
side‑effect‑free except for database access.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Sequence

from sqlalchemy import select

from ..extensions import db
from ..models import Reading


def load_recent_readings(window_seconds: int) -> List[Reading]:
    """
    Load readings from the database within the last `window_seconds`.
    Sorted ascending by timestamp.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)

    stmt = select(Reading).filter(Reading.timestamp >= cutoff).order_by(Reading.timestamp.asc())

    readings: Sequence[Reading] = db.session.execute(stmt).scalars().all()
    return list(readings)


def summarize_readings(readings: Iterable[Reading]) -> Dict[str, Any]:
    """
    Compute JSON‑safe summary statistics for a list of Reading objects.

    Returns:
        {
            "count": int,
            "min_cps": float | None,
            "max_cps": float | None,
            "avg_cps": float | None,
            "window_start": datetime | None,
            "window_end": datetime | None,
        }
    """
    readings_list = list(readings)

    if not readings_list:
        return {
            "count": 0,
            "min_cps": None,
            "max_cps": None,
            "avg_cps": None,
            "window_start": None,
            "window_end": None,
        }

    cps_values = [r.counts_per_second for r in readings_list]
    timestamps = [r.timestamp for r in readings_list]

    count = len(readings_list)
    min_cps = min(cps_values)
    max_cps = max(cps_values)
    avg_cps = sum(cps_values) / count

    window_start = min(timestamps)
    window_end = max(timestamps)

    return {
        "count": count,
        "min_cps": min_cps,
        "max_cps": max_cps,
        "avg_cps": avg_cps,
        "window_start": window_start,
        "window_end": window_end,
    }
