# filename: tests/fixtures/analytics.py

import datetime as dt

import pytest


@pytest.fixture
def ts_base():
    return dt.datetime(2020, 1, 1, 0, 0, 0, tzinfo=dt.timezone.utc)


@pytest.fixture
def shift():
    def _shift(ts: dt.datetime, seconds: int) -> dt.datetime:
        return ts + dt.timedelta(seconds=seconds)

    return _shift
