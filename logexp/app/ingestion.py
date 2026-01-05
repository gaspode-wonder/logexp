# filename: logexp/app/ingestion.py

"""
Compatibility shim for legacy import paths.

Tests and legacy code import ingest_readings from this module.
The real implementation lives in logexp.app.services.ingestion.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from logexp.app.services.ingestion import ingest_reading


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


ingest_batch = ingest_readings
