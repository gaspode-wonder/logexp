# filename: logexp/poller.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import serial

logger = logging.getLogger("logexp.poller")


Frame = Dict[str, Any]


class Poller:
    """
    Step 11E — Poller implementation.

    Responsibilities:
      - Deterministic fake-frame provider (test-safe)
      - Optional real serial frame provider
      - Diagnostics tracking
      - Respect POLLING_ENABLED
      - Deterministic poll_forever() loop
    """

    def __init__(self, config: Dict[str, Any], ingestion: Any) -> None:
        self.config = config
        self.ingestion = ingestion

        # Diagnostics state (11E‑6)
        self.last_frame: Optional[Frame] = None
        self.frames_ingested: int = 0
        self.frames_failed: int = 0
        self.frames_skipped: int = 0

    # ------------------------------------------------------------
    # 11E‑7: Polling enabled flag
    # ------------------------------------------------------------
    def is_enabled(self) -> bool:
        """
        Return True if polling is enabled according to config.

        Default is True to preserve prior behavior unless explicitly disabled.
        """
        enabled = self.config.get("POLLING_ENABLED", True)
        return bool(enabled)

    # ------------------------------------------------------------
    # 11E‑5: Real serial frame provider
    # ------------------------------------------------------------
    def read_serial_frame(self) -> Optional[Frame]:
        port: Optional[str] = self.config.get("SERIAL_PORT")
        baudrate: int = int(self.config.get("SERIAL_BAUDRATE", 9600))
        timeout: float = float(self.config.get("SERIAL_TIMEOUT", 1.0))

        if not port:
            logger.error("SERIAL_PORT not configured; cannot read frame from serial.")
            return None

        try:
            with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
                raw_bytes: bytes = ser.readline()
        except serial.SerialException as exc:
            logger.exception("SerialException on port %s: %s", port, exc)
            return None
        except OSError as exc:
            logger.exception("OS error on port %s: %s", port, exc)
            return None

        if not raw_bytes:
            logger.warning("Empty frame read from serial port %s", port)
            return None

        raw_text = raw_bytes.decode("utf-8", errors="replace").strip()
        return {"raw": raw_text}

    # ------------------------------------------------------------
    # 11E‑2 + 11E‑5: Deterministic frame provider
    # ------------------------------------------------------------
    def get_frame(self) -> Optional[Frame]:
        use_fake: bool = bool(self.config.get("USE_FAKE_FRAMES", True))

        if use_fake:
            fake_value: Any = self.config.get("FAKE_FRAME_VALUE", 42)
            return {"value": fake_value}

        return self.read_serial_frame()

    # ------------------------------------------------------------
    # 11E‑2 + 11E‑6 + 11E‑7: poll_once()
    # ------------------------------------------------------------
    def poll_once(self) -> Optional[Frame]:
        if not self.is_enabled():
            logger.info("Polling disabled by config; poll_once() will not poll.")
            return None

        frame = self.get_frame()

        if frame is None:
            logger.warning("poll_once() obtained no frame; skipping ingestion.")
            self.frames_skipped += 1
            self.last_frame = None
            return None

        try:
            self.ingestion.ingest(frame)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error during ingestion of frame %r: %s", frame, exc)
            self.frames_failed += 1
            self.last_frame = frame
            return None

        self.frames_ingested += 1
        self.last_frame = frame
        return frame

    # ------------------------------------------------------------
    # 11E‑3 + 11E‑7: poll_forever()
    # ------------------------------------------------------------
    def poll_forever(self) -> None:
        if not self.is_enabled():
            logger.info("Polling disabled by config; poll_forever() will not poll.")
            return

        max_frames: int = int(self.config.get("MAX_FRAMES", 10))
        for _ in range(max_frames):
            self.poll_once()

    # ------------------------------------------------------------
    # 11E‑6: Diagnostics surface
    # ------------------------------------------------------------
    def get_diagnostics(self) -> Dict[str, Any]:
        mode = "fake" if self.config.get("USE_FAKE_FRAMES", True) else "serial"

        return {
            "mode": mode,
            "last_frame": self.last_frame,
            "frames_ingested": self.frames_ingested,
            "frames_failed": self.frames_failed,
            "frames_skipped": self.frames_skipped,
            "serial": {
                "port": self.config.get("SERIAL_PORT"),
                "baudrate": self.config.get("SERIAL_BAUDRATE", 9600),
                "timeout": self.config.get("SERIAL_TIMEOUT", 1.0),
            },
        }
