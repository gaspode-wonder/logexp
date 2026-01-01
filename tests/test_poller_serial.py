# tests/test_poller_serial.py

import types

import pytest


class DummyIngestion:
    def __init__(self):
        self.calls = []

    def ingest(self, frame):
        self.calls.append(frame)


def test_poll_once_uses_fake_frames_by_default():
    from logexp.poller import Poller

    ingestion = DummyIngestion()
    config = {}  # USE_FAKE_FRAMES defaults to True

    p = Poller(config, ingestion)
    frame = p.poll_once()

    assert frame == {"value": 42}
    assert ingestion.calls == [{"value": 42}]


def test_poll_once_fake_frame_custom_value():
    from logexp.poller import Poller

    ingestion = DummyIngestion()
    config = {"FAKE_FRAME_VALUE": 123}

    p = Poller(config, ingestion)
    frame = p.poll_once()

    assert frame == {"value": 123}
    assert ingestion.calls == [{"value": 123}]


def test_poll_once_real_serial_success(monkeypatch):
    from logexp.poller import Poller

    ingestion = DummyIngestion()

    # Fake serial object
    class FakeSerial:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def readline(self):
            return b"123\n"

    monkeypatch.setattr("serial.Serial", FakeSerial)

    config = {
        "USE_FAKE_FRAMES": False,
        "SERIAL_PORT": "/dev/ttyUSB0",
    }

    p = Poller(config, ingestion)
    frame = p.poll_once()

    assert frame == {"raw": "123"}
    assert ingestion.calls == [{"raw": "123"}]


def test_poll_once_real_serial_missing_port(caplog):
    from logexp.poller import Poller

    ingestion = DummyIngestion()
    config = {"USE_FAKE_FRAMES": False}  # SERIAL_PORT missing

    p = Poller(config, ingestion)
    frame = p.poll_once()

    assert frame is None
    assert ingestion.calls == []
    assert any("SERIAL_PORT not configured" in m for m in caplog.text.splitlines())


def test_read_serial_frame_handles_serial_exception(monkeypatch, caplog):
    import serial

    from logexp.poller import Poller

    ingestion = DummyIngestion()

    def fake_serial(*a, **kw):
        raise serial.SerialException("boom")

    monkeypatch.setattr("serial.Serial", fake_serial)

    config = {
        "USE_FAKE_FRAMES": False,
        "SERIAL_PORT": "/dev/ttyUSB0",
    }

    p = Poller(config, ingestion)
    frame = p.read_serial_frame()

    assert frame is None
    assert "SerialException" in caplog.text


def test_poll_once_ingestion_exception_is_logged(caplog):
    from logexp.poller import Poller

    class BadIngestion:
        def ingest(self, frame):
            raise RuntimeError("ingestion failed")

    ingestion = BadIngestion()
    config = {}

    p = Poller(config, ingestion)
    frame = p.poll_once()

    assert frame is None
    assert "ingestion failed" in caplog.text


def test_poll_forever_calls_poll_once(monkeypatch):
    from logexp.poller import Poller

    ingestion = DummyIngestion()
    config = {"MAX_FRAMES": 3}

    p = Poller(config, ingestion)

    calls = {"count": 0}

    def fake_poll_once():
        calls["count"] += 1

    monkeypatch.setattr(p, "poll_once", fake_poll_once)

    p.poll_forever()

    assert calls["count"] == 3
