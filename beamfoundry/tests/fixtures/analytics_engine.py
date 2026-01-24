# filename: tests/fixtures/analytics_engine.py

import pytest

from beamfoundry.analytics.engine import AnalyticsEngine


@pytest.fixture
def analytics_engine():
    """
    Provide the compatibility AnalyticsEngine class required by the test suite.
    """
    return AnalyticsEngine(window_minutes=5)
