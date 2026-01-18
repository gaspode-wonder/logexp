"""
Compatibility shim for legacy import paths.

Modern ingestion lives in logexp.app.services.ingestion.
This module ONLY provides:
  - legacy payload normalization
  - legacy payload translation
  - ingest_readings() / ingest_batch() compatibility wrappers

It no longer exposes API endpoints or serializers.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from logexp.app.services.ingestion import ingest_reading

# ---------------------------------------------------------------------------
# Legacy payload normalization + translation
# ---------------------------------------------------------------------------


def _normalize_readings_arg(arg: Any) -> List[Dict[str, Any]]:
    """
    Normalize various legacy call shapes into a list of dict payloads.

    Supported shapes:
      - dict → [dict]
      - iterable of dicts → list(dict)
      - None → []
    """
    if arg is None:
        return []

    if isinstance(arg, dict):
        return [arg]

    if isinstance(arg, Iterable):
        return list(arg)

    return []


def _translate_legacy_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate legacy ingestion payloads into the canonical ingestion format.

    Legacy tests may pass:
        {"value": X}

    Canonical ingestion requires:
        {
            "counts_per_second": ...,
            "counts_per_minute": ...,
            "microsieverts_per_hour": ...,
            "mode": ...
        }
    """
    if "counts_per_second" in payload:
        return payload

    value = payload.get("value")

    return {
        "counts_per_second": value,
        "counts_per_minute": value,
        "microsieverts_per_hour": value,
        "mode": "legacy",
    }


# ---------------------------------------------------------------------------
# Legacy ingestion entrypoints
# ---------------------------------------------------------------------------


def ingest_readings(*args: Any, **kwargs: Any) -> List[Any]:
    """
    Legacy API: ingest a list of payloads.

    Supported call styles:
      - ingest_readings([...])
      - ingest_readings(readings=[...])
      - ingest_readings(readings={...})
      - ingest_readings([...], cutoff_ts=..., extra=...)

    All extra kwargs (including cutoff_ts) are ignored.
    """
    if "readings" in kwargs:
        raw = kwargs["readings"]
    elif args:
        raw = args[0]
    else:
        raw = None

    raw_list = _normalize_readings_arg(raw)
    translated = [_translate_legacy_payload(p) for p in raw_list]

    results: List[Any] = []
    for payload in translated:
        results.append(ingest_reading(payload))

    return results


# Backwards compatibility alias
ingest_batch = ingest_readings

__all__ = ["ingest_reading", "ingest_readings", "ingest_batch"]
