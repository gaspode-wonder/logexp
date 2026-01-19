# filename: tests/unit/poller/test_ingestion_errors.py

from poller_config import PollerConfig

from tests.fixtures.poller.fake_ingestion import FakeIngestion


def test_ingestion_error_increments_counters(make_poller):
    failing = FakeIngestion(should_fail=True)

    poller = make_poller(
        config=PollerConfig(
            mode="fake",
            fake_frame_value=7,
        ),
        ingestion=failing,
    )

    frame = poller.poll_once()

    # Poller returns the frame even if ingestion fails
    assert frame == {"raw": "7"}

    # Ingestion-level counters
    assert failing.frames == [frame]
    assert failing.failures == 1

    # Poller diagnostics should see zero successfully ingested frames
    diag = poller.get_diagnostics()
    assert diag["frames_ingested"] == 0
