# filename: tests/test_poller_diagnostics.py

from logexp.poller import Poller


class BadIngestion:
    def ingest(self, frame):
        raise RuntimeError("boom")


def test_diagnostics_after_ingestion_failure(caplog):
    poller = Poller(
        {"USE_FAKE_FRAMES": True, "MAX_FRAMES": 1}, ingestion=BadIngestion()
    )
    poller.poll_forever()

    # Structured logging event name
    assert "ingestion_error" in caplog.text

    diag = poller.get_diagnostics()
    assert diag["ingestion_failures"] == 1
