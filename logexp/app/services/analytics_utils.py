# logexp/app/services/analytics_utils.py


def moving_average(values, smoothing_factor):
    """
    Compute an exponential moving average (EMA) over a list of numeric values.
    """
    if not values:
        return None

    ema = values[0]
    for v in values[1:]:
        ema = (smoothing_factor * v) + ((1 - smoothing_factor) * ema)

    return ema


def average(values):
    """
    Simple arithmetic mean.
    """
    if not values:
        return None
    return sum(values) / len(values)


def extract_field(readings, field):
    """
    Extract a numeric field from a list of ORM objects.
    """
    return [getattr(r, field) for r in readings]


def summarize_readings(readings):
    """
    Produce a lightweight diagnostic summary for debugging.
    Not part of the analytics diagnostics contract.
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
