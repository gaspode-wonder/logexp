# filename: logexp/app/services/analytics_utils.py

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from ..logging_setup import get_logger

logger = get_logger("beamfoundry.analytics")


def moving_average(values: Iterable[float], smoothing_factor: float) -> Optional[float]:
    """
    Compute an exponential moving average (EMA) over a list of numeric values.
    """
    values_list: List[float] = list(values)
    if not values_list:
        logger.debug("analytics_utils_moving_average_empty")
        return None

    ema: float = values_list[0]
    for v in values_list[1:]:
        ema = (smoothing_factor * v) + ((1 - smoothing_factor) * ema)

    logger.debug(
        "analytics_utils_moving_average_computed",
        extra={"count": len(values_list), "ema": ema},
    )

    return ema


def average(values: Iterable[float]) -> Optional[float]:
    """
    Simple arithmetic mean.
    """
    values_list: List[float] = list(values)
    if not values_list:
        logger.debug("analytics_utils_average_empty")
        return None

    avg = sum(values_list) / len(values_list)

    logger.debug(
        "analytics_utils_average_computed",
        extra={"count": len(values_list), "average": avg},
    )

    return avg


def extract_field(readings: Iterable[Any], field: str) -> List[Any]:
    """
    Extract a numeric field from a list of ORM objects.
    """
    readings_list = list(readings)
    extracted = [getattr(r, field) for r in readings_list]

    logger.debug(
        "analytics_utils_extract_field",
        extra={"field": field, "count": len(extracted)},
    )

    return extracted


def summarize_readings(readings: Iterable[Any]) -> Dict[str, Any]:
    """
    Produce a lightweight diagnostic summary for debugging.
    Not part of the analytics diagnostics contract.
    """
    readings_list: List[Any] = list(readings)
    if not readings_list:
        logger.debug("analytics_utils_summarize_empty")
        return {"count": 0}

    summary = {
        "count": len(readings_list),
        "first_timestamp": readings_list[0].timestamp,
        "last_timestamp": readings_list[-1].timestamp,
        "min_cps": min(r.counts_per_second for r in readings_list),
        "max_cps": max(r.counts_per_second for r in readings_list),
    }

    logger.debug(
        "analytics_utils_summarize_computed",
        extra={
            "count": summary["count"],
            "first_timestamp": summary["first_timestamp"].isoformat(),
            "last_timestamp": summary["last_timestamp"].isoformat(),
            "min_cps": summary["min_cps"],
            "max_cps": summary["max_cps"],
        },
    )

    return summary
