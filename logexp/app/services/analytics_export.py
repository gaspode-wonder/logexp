# filename: logexp/app/services/analytics_export.py

from __future__ import annotations

import csv
from io import StringIO
from typing import Any, Iterable


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
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["timestamp", "counts_per_second"])

    for r in readings:
        writer.writerow([r.timestamp.isoformat(), r.counts_per_second])

    return output.getvalue()
