# filename: logexp/poller_config.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

Mode = Literal["fake", "serial"]


@dataclass
class PollerConfig:
    """
    Unified configuration surface for the Poller.

    - mode:
        * "fake"   -> deterministic fake frames
        * "serial" -> real serial port (or patched FakeSerial in tests)
    - polling_enabled:
        * if False, poll_once/poll_forever are no-ops
    - fake_frame_value:
        * value used by fake mode, exposed as {"raw": str(fake_frame_value)}
    - max_frames:
        * upper bound for poll_forever loops (None means unbounded)
    """

    mode: Mode
    polling_enabled: bool = True

    # Fake mode
    fake_frame_value: int = 42

    # Serial mode
    serial_port: Optional[str] = None
    serial_baudrate: int = 9600
    serial_timeout: float = 1.0

    # Shared
    max_frames: Optional[int] = 5
