# filename: tests/unit/poller/test_serial_frames.py

from __future__ import annotations

from typing import Any, Iterable

from logexp.poller_config import PollerConfig


def _make_serial_poller(make_poller, fake_items: Iterable[Any]):
    """
    Helper to construct a serial-mode Poller using the unified PollerConfig.
    Ensures a dummy serial_port is provided so the Poller enters serial mode.
    """
    return make_poller(
        config=PollerConfig(
            mode="serial",
            serial_port="/dev/ttyFAKE",
        ),
        fake_serial_items=fake_items,
    )


def test_serial_frame_success(make_poller):
    poller = _make_serial_poller(make_poller, [b"HELLO\n"])

    frame = poller.poll_once()

    assert frame == {"raw": "HELLO"}

    diag = poller.get_diagnostics()
    assert diag["mode"] == "serial"
    assert diag["frames_ingested"] == 1


def test_serial_empty_frame_skipped(make_poller):
    poller = _make_serial_poller(make_poller, [b""])

    frame = poller.poll_once()

    assert frame is None

    diag = poller.get_diagnostics()
    assert diag["mode"] == "serial"
    assert diag["frames_ingested"] == 0
