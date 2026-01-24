# filename: logexp/app/services/analytics_diagnostics.py

from __future__ import annotations

from typing import Any, Dict

from flask import current_app

from ..logging_setup import get_logger
from ..services.analytics_readings import load_recent_readings, summarize_readings

logger = get_logger("beamfoundry.analytics_diagnostics")


def run_analytics_diagnostics() -> Dict[str, Any]:
    window_seconds: int = current_app.config.get("ANALYTICS_WINDOW_SECONDS", 60)
    window_minutes: int = window_seconds // 60

    readings = load_recent_readings(window_seconds)
    summary = summarize_readings(readings)

    # Convert datetimes (or None) to ISO strings
    ws = summary["window_start"]
    we = summary["window_end"]

    window_start_str = ws.isoformat() if ws is not None else ""
    window_end_str = we.isoformat() if we is not None else ""

    result: Dict[str, Any] = {
        "count": summary["count"],
        "min_cps": summary["min_cps"],
        "max_cps": summary["max_cps"],
        "avg_cps": summary["avg_cps"],
        "window_start": window_start_str,
        "window_end": window_end_str,
        "window_minutes": window_minutes,
    }

    logger.debug("analytics_diagnostics_complete", extra=result)
    return result


def get_analytics_status() -> Dict[str, Any]:
    return run_analytics_diagnostics()
