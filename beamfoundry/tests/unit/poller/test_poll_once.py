# filename: tests/unit/poller/test_poll_once.py

from beamfoundry.poller import Poller
from poller_config import PollerConfig
from tests.fixtures.poller.fake_ingestion import FakeIngestion


def test_poll_once_returns_none_when_disabled():
    config = PollerConfig(mode="fake", polling_enabled=False)
    ingestion = FakeIngestion()
    poller = Poller(config=config, ingestion=ingestion)

    frame = poller.poll_once()

    assert frame is None
    assert ingestion.frames == []

    diag = poller.get_diagnostics()
    assert diag["frames_ingested"] == 0
    assert diag["polling_enabled"] is False
