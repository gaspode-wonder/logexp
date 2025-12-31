# logexp/app/services/analytics_diagnostics.py


def summarize_readings(readings):
    """
    Produce a lightweight diagnostic summary for debugging.
    """
    if not readings:
        return {"count": 0}

    return {
        "count": len(readings),
        "first_timestamp": readings[0].timestamp,
        "last_timestamp": readings[-1].timestamp,
        "min_cps": min(r.counts_per_second for r in readings),
        "max_cps": max(r.counts_per_second for r in readings),
    }
