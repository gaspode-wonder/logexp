from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.logging_setup import get_logger

from .engine import AnalyticsEngine, AnalyticsResult, ReadingSample

logger = get_logger("beamfoundry.analytics")


# ---------------------------------------------------------------------------
# Pure Analytics Diagnostics
# ---------------------------------------------------------------------------


def get_analytics_status(
    window_minutes: int,
    samples: List[ReadingSample],
    now: datetime,
) -> Dict[str, Any]:
    """
    Pure analytics diagnostics function.

    - No Flask
    - No SQLAlchemy
    - No config imports
    - Deterministic and JSON‑safe
    """
    logger.debug(
        "analytics_diagnostics_requested",
        extra={
            "window_minutes": window_minutes,
            "sample_count": len(samples),
            "now": now.isoformat(),
        },
    )

    engine = AnalyticsEngine(window_minutes=window_minutes)
    logger.debug(
        "analytics_diagnostics_engine_created",
        extra={"window_minutes": window_minutes},
    )

    engine.add_readings(samples)
    logger.debug(
        "analytics_diagnostics_samples_added",
        extra={"count": len(samples)},
    )

    result: AnalyticsResult = engine.compute_metrics(now=now)

    window_start = result.window_start.isoformat() if result.window_start else None
    window_end = result.window_end.isoformat() if result.window_end else None

    logger.debug(
        "analytics_diagnostics_metrics_computed",
        extra={
            "count": result.count,
            "average": result.average,
            "minimum": result.minimum,
            "maximum": result.maximum,
            "window_start": window_start,
            "window_end": window_end,
        },
    )

    payload: Dict[str, Any] = asdict(result)
    payload["window_start"] = window_start
    payload["window_end"] = window_end

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
) -> Dict[str, Any]:
    """
    Pure database diagnostics formatter.

    The service layer (Flask-aware) gathers DB information and passes it here.
    This function simply formats it into a JSON‑safe payload.
    """
    last_ts = last_reading_at.isoformat() if last_reading_at else None

    logger.debug(
        "database_diagnostics_requested",
        extra={
            "uri": uri,
            "engine": engine,
            "connected": connected,
            "readings_count": readings_count,
            "last_reading_at": last_ts,
            "migration_revision": migration_revision,
            "schema_ok": schema_ok,
        },
    )

    return {
        "uri": uri,
        "engine": engine,
        "connected": connected,
        "readings_count": readings_count,
        "last_reading_at": last_ts,
        "migration_revision": migration_revision,
        "schema_ok": schema_ok,
    }
