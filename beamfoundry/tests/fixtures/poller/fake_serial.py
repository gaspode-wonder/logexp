# filename: tests/fixtures/poller/fake_serial.py

from __future__ import annotations

from typing import Any, Iterable, List

import serial


class FakeSerial:
    """
    Deterministic fake serial port.

    Accepts a sequence of items. Each call to .readline() consumes one item:

    - if the item is bytes → returned as the frame
    - if the item is a BaseException → raised
    """

    def __init__(
        self,
        frames_or_errors: Iterable[Any],
        port: str = "FAKE",
        baudrate: int = 9600,
        timeout: float = 1.0,
    ) -> None:
        self.items: List[Any] = list(frames_or_errors)
        self.index: int = 0
        self.port: str = port
        self.baudrate: int = baudrate
        self.timeout: float = timeout

    # Context manager API used by Poller.read_serial_frame
    def __enter__(self) -> "FakeSerial":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        # No special cleanup needed
        return None

    def readline(self) -> bytes:
        if self.index >= len(self.items):
            # Simulate timeout / no data
            return b""

        item = self.items[self.index]
        self.index += 1

        if isinstance(item, BaseException):
            raise item

        if isinstance(item, bytes):
            return item

        # For safety in tests, allow str and convert to bytes
        if isinstance(item, str):
            return item.encode("utf-8")

        # Anything else is a test bug
        raise TypeError(f"Unsupported fake serial item: {item!r}")


def make_serial_with_frames(frames: Iterable[bytes]) -> FakeSerial:
    """Convenience helper: FakeSerial that only returns frames."""
    return FakeSerial(frames_or_errors=frames)


def make_serial_with_errors(items: Iterable[Any]) -> FakeSerial:
    """
    Convenience helper: FakeSerial with a mix of frames and exceptions.

    Example:
        make_serial_with_errors([
            b"OK\n",
            serial.SerialException("boom"),
            b"OK\n",
        ])
    """
    return FakeSerial(frames_or_errors=items)


def serial_exception(message: str = "fake serial error") -> serial.SerialException:
    """Helper to construct a SerialException with a stable message."""
    return serial.SerialException(message)
