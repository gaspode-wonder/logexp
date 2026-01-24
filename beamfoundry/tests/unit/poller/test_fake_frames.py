# filename: tests/unit/poller/test_fake_frames.py

from poller_config import PollerConfig
from tests.fixtures.poller.fake_ingestion import FakeIngestion


def test_poll_once_uses_fake_frame_by_default(make_poller):
    ingestion = FakeIngestion()
    poller = make_poller(
        config=PollerConfig(
            mode="fake",
            fake_frame_value=123,
        ),
        ingestion=ingestion,
    )

    frame = poller.poll_once()

    assert frame == {"raw": "123"}
    assert ingestion.frames == [frame]

    diag = poller.get_diagnostics()
    assert diag["frames_ingested"] == 1
    assert diag["mode"] == "fake"
