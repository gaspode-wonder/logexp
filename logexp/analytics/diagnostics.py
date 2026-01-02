# logexp/analytics/diagnostics.py

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import List, Optional

from .engine import AnalyticsEngine, AnalyticsResult, ReadingSample


# ---------------------------------------------------------------------------
# Pure Analytics Diagnostics
# ---------------------------------------------------------------------------
def get_analytics_status(
    window_minutes: int,
    samples: List[ReadingSample],
    now: datetime,
) -> dict:
    """
    Pure analytics diagnostics function.

    - No Flask
    - No SQLAlchemy
    - No config imports
    - Deterministic and JSON‑safe
    """
    engine = AnalyticsEngine(window_minutes=window_minutes)
    engine.add_readings(samples)

    result: AnalyticsResult = engine.compute_metrics(now=now)

    payload = asdict(result)
    payload["window_start"] = payload["window_start"].isoformat()
    payload["window_end"] = payload["window_end"].isoformat()

    return payload


# ---------------------------------------------------------------------------
# Pure Database Diagnostics
# ---------------------------------------------------------------------------
def get_database_status(
    *,
    uri: Optional[str],
    engine: Optional[str],
    connected: bool,
    readings_count: Optional[int],
    last_reading_at: Optional[datetime],
    migration_revision: Optional[str],
    schema_ok: bool,
) -> dict:
    """
    Pure database diagnostics formatter.

    The service layer (Flask-aware) gathers DB information and passes it here.
    This function simply formats it into a JSON‑safe payload.
    """
    return {
        "uri": uri,
        "engine": engine,
        "connected": connected,
        "readings_count": readings_count,
        "last_reading_at": (last_reading_at.isoformat() if last_reading_at else None),
        "migration_revision": migration_revision,
        "schema_ok": schema_ok,
    }
