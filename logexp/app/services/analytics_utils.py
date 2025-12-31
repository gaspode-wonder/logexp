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
