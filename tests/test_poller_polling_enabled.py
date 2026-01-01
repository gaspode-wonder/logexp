# tests/test_poller_polling_enabled.py


def test_poll_once_respects_polling_disabled(monkeypatch):
    from logexp.poller import Poller

    class DummyIngestion:
        def __init__(self):
            self.calls = []

        def ingest(self, frame):
            self.calls.append(frame)

    config = {
        "POLLING_ENABLED": False,
    }
    ingestion = DummyIngestion()
    p = Poller(config, ingestion)

    # Even if get_frame() would normally return a frame, polling should not occur
    monkeypatch.setattr(p, "get_frame", lambda: {"value": 123})

    result = p.poll_once()

    assert result is None
    assert ingestion.calls == []
    d = p.get_diagnostics()
    assert d["frames_ingested"] == 0
    assert d["frames_failed"] == 0
    assert d["frames_skipped"] == 0
    assert d["last_frame"] is None


def test_poll_forever_respects_polling_disabled(monkeypatch):
    from logexp.poller import Poller

    class DummyIngestion:
        def __init__(self):
            self.calls = []

        def ingest(self, frame):
            self.calls.append(frame)

    config = {
        "POLLING_ENABLED": False,
        "MAX_FRAMES": 5,
    }
    ingestion = DummyIngestion()
    p = Poller(config, ingestion)

    # If poll_forever() ignored POLLING_ENABLED, this would be called 5 times
    monkeypatch.setattr(p, "get_frame", lambda: {"value": 123})

    p.poll_forever()

    assert ingestion.calls == []
    d = p.get_diagnostics()
    assert d["frames_ingested"] == 0
    assert d["frames_failed"] == 0
    assert d["frames_skipped"] == 0
    assert d["last_frame"] is None


def test_polling_enabled_default_true(monkeypatch):
    from logexp.poller import Poller

    class DummyIngestion:
        def __init__(self):
            self.calls = []

        def ingest(self, frame):
            self.calls.append(frame)

    # No POLLING_ENABLED in config → default True
    config = {}
    ingestion = DummyIngestion()
    p = Poller(config, ingestion)

    monkeypatch.setattr(p, "get_frame", lambda: {"value": 123})

    p.poll_once()

    assert len(ingestion.calls) == 1
    d = p.get_diagnostics()
    assert d["frames_ingested"] == 1
    assert d["last_frame"] == {"value": 123}
