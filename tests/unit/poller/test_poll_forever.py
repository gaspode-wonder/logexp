# filename: tests/unit/poller/test_poll_forever.py

from poller_config import PollerConfig

from tests.fixtures.poller.fake_ingestion import FakeIngestion


def test_poll_forever_honors_max_frames(make_poller):
    ingestion = FakeIngestion()
    poller = make_poller(
        config=PollerConfig(
            mode="fake",
            fake_frame_value=99,
            max_frames=5,
        ),
        ingestion=ingestion,
    )

    poller.poll_forever()

    # Ingestion should receive exactly max_frames frames
    assert len(ingestion.frames) == 5
    for frame in ingestion.frames:
        assert frame == {"raw": "99"}

    diag = poller.get_diagnostics()
    assert diag["frames_ingested"] == 5


def test_poll_forever_disabled_does_nothing(make_poller):
    ingestion = FakeIngestion()
    poller = make_poller(
        config=PollerConfig(
            mode="fake",
            polling_enabled=False,
        ),
        ingestion=ingestion,
    )

    poller.poll_forever()

    # No frames ingested when polling is disabled
    assert ingestion.frames == []
    diag = poller.get_diagnostics()
    assert diag["frames_ingested"] == 0
    assert diag["polling_enabled"] is False
