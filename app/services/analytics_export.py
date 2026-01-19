# filename: logexp/app/services/analytics_export.py

from __future__ import annotations

import csv
from io import StringIO
from typing import Any, Iterable

from app.logging_setup import get_logger

logger = get_logger("logexp.analytics")


def export_readings_to_csv(readings: Iterable[Any]) -> str:
    """
    Export readings to CSV for download.

    Each reading is expected to have:
        - timestamp: datetime with .isoformat()
        - counts_per_second: numeric

    Args:
        readings: Iterable of ORM reading objects.

    Returns:
        str: CSV-formatted string.
    """
    readings_list = list(readings)

    logger.debug(
        "analytics_export_start",
        extra={"row_count": len(readings_list)},
    )

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["timestamp", "counts_per_second"])

    for r in readings_list:
        writer.writerow([r.timestamp.isoformat(), r.counts_per_second])

    csv_data = output.getvalue()

    logger.debug(
        "analytics_export_complete",
        extra={"bytes": len(csv_data)},
    )

    return csv_data
