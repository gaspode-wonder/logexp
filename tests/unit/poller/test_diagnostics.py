# filename: tests/unit/poller/test_diagnostics.py

from logexp.poller_config import PollerConfig


def test_diagnostics_fake_mode(make_poller):
    poller = make_poller(
        config=PollerConfig(
            mode="fake",
            fake_frame_value=5,
        ),
    )

    poller.poll_once()
    diag = poller.get_diagnostics()

    assert diag["mode"] == "fake"
    assert diag["polling_enabled"] is True
    assert diag["frames_ingested"] == 1
    # Fake mode has no serial section
    assert "serial" not in diag


def test_diagnostics_serial_mode(make_poller):
    poller = make_poller(
        config=PollerConfig(
            mode="serial",
            serial_port="/dev/ttyFAKE",
        ),
        fake_serial_items=[b"OK\n"],
    )

    poller.poll_once()
    diag = poller.get_diagnostics()

    assert diag["mode"] == "serial"
    assert diag["polling_enabled"] is True
    assert diag["frames_ingested"] == 1
    assert "serial" in diag
    assert diag["serial"]["port"] == "/dev/ttyFAKE"
