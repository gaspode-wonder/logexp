# filename: logexp/app/ingestion.py

"""
Compatibility shim for legacy import paths.

Tests and legacy code import ingest_readings from this module.
The real implementation lives in logexp.app.services.ingestion.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from flask import Blueprint, jsonify
from flask.typing import ResponseReturnValue

from logexp.app.extensions import db
from logexp.app.models import LogExpReading
from logexp.app.services.ingestion import ingest_reading

# ---------------------------------------------------------------------------
# Blueprint for ingestion-related API endpoints
# ---------------------------------------------------------------------------

bp = Blueprint("ingestion_api", __name__, url_prefix="/api")


@bp.get("/readings/latest")
def get_latest_reading() -> ResponseReturnValue:
    """
    Return the most recent reading stored in the database.
    """
    row = db.session.query(LogExpReading).order_by(LogExpReading.timestamp.desc()).first()

    if row is None:
        return jsonify({"error": "no readings available"}), 404

    return jsonify(
        {
            "id": row.id,
            "timestamp": row.timestamp.isoformat(),
            "counts_per_second": row.counts_per_second,
            "counts_per_minute": row.counts_per_minute,
            "microsieverts_per_hour": row.microsieverts_per_hour,
            "mode": row.mode,
            "node_id": row.node_id,
        }
    )


# ---------------------------------------------------------------------------
# Legacy ingestion shim
# ---------------------------------------------------------------------------


def _normalize_readings_arg(arg: Any) -> List[Dict[str, Any]]:
    """
    Normalize various test/legacy call shapes into a list of dict payloads.
    """
    if arg is None:
        return []

    # Single dict → [dict]
    if isinstance(arg, dict):
        return [arg]

    # Iterable of dicts
    if isinstance(arg, Iterable):
        return list(arg)

    return []


def _translate_legacy_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate legacy ingestion payloads into the canonical ingestion format.

    Tests pass payloads like:
        {"value": 1}

    The ingestion service expects:
        {
            "counts_per_second": ...,
            "counts_per_minute": ...,
            "microsieverts_per_hour": ...,
            "mode": ...
        }
    """
    if "counts_per_second" in payload:
        # Already canonical
        return payload

    # Legacy format: {"value": X}
    value = payload.get("value")

    return {
        "counts_per_second": value,
        "counts_per_minute": value,
        "microsieverts_per_hour": value,
        "mode": "legacy",
    }


def ingest_readings(*args: Any, **kwargs: Any) -> List[Any]:
    """
    Legacy API: ingest a list of payloads.

    Supported call styles:
      - ingest_readings([...])
      - ingest_readings(readings=[...])
      - ingest_readings(readings={...})
      - ingest_readings([...], cutoff_ts=..., extra=...)

    All extra kwargs (including cutoff_ts) are ignored here.
    """
    if "readings" in kwargs:
        raw = kwargs["readings"]
    elif args:
        raw = args[0]
    else:
        raw = None

    raw_list = _normalize_readings_arg(raw)

    # Translate legacy payloads into canonical ingestion payloads
    translated = [_translate_legacy_payload(p) for p in raw_list]

    results: List[Any] = []
    for payload in translated:
        result = ingest_reading(payload)
        results.append(result)

    return results


# Backwards compatibility alias
ingest_batch = ingest_readings

__all__ = ["ingest_reading", "ingest_readings", "ingest_batch", "bp"]
