# logexp/app/services/analytics_export.py

import csv
from io import StringIO


def export_readings_to_csv(readings):
    """
    Export readings to CSV for download.
    """
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "counts_per_second"])

    for r in readings:
        writer.writerow([r.timestamp.isoformat(), r.counts_per_second])

    return output.getvalue()
