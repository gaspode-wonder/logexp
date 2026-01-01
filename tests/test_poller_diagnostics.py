# tests/test_poller_diagnostics.py


def test_diagnostics_initial_state():
    from logexp.poller import Poller

    class DummyIngestion:
        def ingest(self, frame):
            pass

    p = Poller({}, DummyIngestion())
    d = p.get_diagnostics()

    assert d["mode"] == "fake"
    assert d["last_frame"] is None
    assert d["frames_ingested"] == 0
    assert d["frames_failed"] == 0
    assert d["frames_skipped"] == 0


def test_diagnostics_after_fake_ingestion():
    from logexp.poller import Poller

    class DummyIngestion:
        def __init__(self):
            self.calls = []

        def ingest(self, frame):
            self.calls.append(frame)

    p = Poller({}, DummyIngestion())
    p.poll_once()

    d = p.get_diagnostics()
    assert d["frames_ingested"] == 1
    assert d["last_frame"] == {"value": 42}


def test_diagnostics_after_skipped_frame(monkeypatch):
    from logexp.poller import Poller

    class DummyIngestion:
        def ingest(self, frame):
            pass

    p = Poller({"USE_FAKE_FRAMES": False}, DummyIngestion())

    monkeypatch.setattr(p, "read_serial_frame", lambda: None)

    p.poll_once()
    d = p.get_diagnostics()

    assert d["frames_skipped"] == 1
    assert d["last_frame"] is None


def test_diagnostics_after_ingestion_failure(caplog):
    from logexp.poller import Poller

    class BadIngestion:
        def ingest(self, frame):
            raise RuntimeError("boom")

    p = Poller({}, BadIngestion())
    p.poll_once()

    d = p.get_diagnostics()
    assert d["frames_failed"] == 1
    assert d["last_frame"] == {"value": 42}
    assert "boom" in caplog.text
