# tests/helpers/analytics.py

# Helper utilities for deterministic analytics tests.
# These are pure functions: no ingestion, no poller, no DB, no Flask.
from typing import Any
import datetime as dt


def ts(year, month, day, hour, minute, second):
    """
    Create a fixed UTC timestamp.
    """
    return dt.datetime(year, month, day, hour, minute, second, tzinfo=dt.timezone.utc)


def shift(ts: dt.datetime, seconds: int) -> dt.datetime:
    """
    Shift a timestamp by N seconds.
    """
    return ts + dt.timedelta(seconds=seconds)


def make_reading(model_cls: Any, ts: dt.datetime, value: float) -> Any:
    """
    Create a Reading instance without DB involvement.
    """
    return model_cls(timestamp=ts, value=value)


def make_batch(model_cls, pairs):
    """
    Create a list of readings from (ts, value) tuples.
    """
    return [make_reading(model_cls, ts, value) for ts, value in pairs]
