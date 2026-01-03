# filename: tests/test_poller_serial.py

from logexp.poller import Poller


def test_poll_once_real_serial_missing_port(caplog):
    poller = Poller({"USE_FAKE_FRAMES": False}, ingestion=lambda f: None)
    poller.poll_once()

    # Structured logging event name
    assert "serial_port_missing" in caplog.text


def test_read_serial_frame_handles_serial_exception(caplog, monkeypatch):
    import serial

    class FakeSerial:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def readline(self):
            raise serial.SerialException("SerialException")

    poller = Poller({"USE_FAKE_FRAMES": False}, ingestion=lambda f: None)

    poller.config["SERIAL_PORT"] = "/dev/fake"

    monkeypatch.setattr(poller, "_open_serial", lambda: FakeSerial())

    poller.read_serial_frame()

    assert "serial_exception" in caplog.text


def test_poll_once_ingestion_exception_is_logged(caplog):
    class BadIngestion:
        def ingest(self, frame):
            raise RuntimeError("boom")

    poller = Poller(
        {"USE_FAKE_FRAMES": True, "MAX_FRAMES": 1}, ingestion=BadIngestion()
    )
    poller.poll_once()

    # Structured logging event name
    assert "ingestion_error" in caplog.text
