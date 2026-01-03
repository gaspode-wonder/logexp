# filename: logexp/poller.py

from __future__ import annotations

from typing import Any, Dict, Optional

import serial

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.poller")

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

        logger.debug(
            "poller_initialized",
            extra={
                "use_fake": self.config.get("USE_FAKE_FRAMES", True),
                "enabled": self.config.get("POLLING_ENABLED", True),
            },
        )

    # ------------------------------------------------------------
    # 11E‑7: Polling enabled flag
    # ------------------------------------------------------------
    def is_enabled(self) -> bool:
        enabled = bool(self.config.get("POLLING_ENABLED", True))
        logger.debug("poller_enabled_check", extra={"enabled": enabled})
        return enabled

    # ------------------------------------------------------------
    # 11E‑5: Real serial frame provider
    # ------------------------------------------------------------
    def read_serial_frame(self) -> Optional[Frame]:
        port: Optional[str] = self.config.get("SERIAL_PORT")
        baudrate: int = int(self.config.get("SERIAL_BAUDRATE", 9600))
        timeout: float = float(self.config.get("SERIAL_TIMEOUT", 1.0))

        logger.debug(
            "serial_read_attempt",
            extra={"port": port, "baudrate": baudrate, "timeout": timeout},
        )

        if not port:
            logger.error("serial_port_missing")
            return None

        try:
            with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
                raw_bytes: bytes = ser.readline()
        except serial.SerialException as exc:
            logger.error(
                "serial_exception",
                extra={"port": port, "error": str(exc)},
            )
            return None
        except OSError as exc:
            logger.error(
                "serial_os_error",
                extra={"port": port, "error": str(exc)},
            )
            return None

        if not raw_bytes:
            logger.warning("serial_empty_frame", extra={"port": port})
            return None

        raw_text = raw_bytes.decode("utf-8", errors="replace").strip()

        logger.debug(
            "serial_frame_read",
            extra={"port": port, "bytes": len(raw_bytes)},
        )

        return {"raw": raw_text}

    # ------------------------------------------------------------
    # 11E‑2 + 11E‑5: Deterministic frame provider
    # ------------------------------------------------------------
    def get_frame(self) -> Optional[Frame]:
        use_fake: bool = bool(self.config.get("USE_FAKE_FRAMES", True))

        if use_fake:
            fake_value: Any = self.config.get("FAKE_FRAME_VALUE", 42)
            logger.debug("fake_frame_generated", extra={"value": fake_value})
            return {"value": fake_value}

        logger.debug("serial_frame_requested")
        return self.read_serial_frame()

    # ------------------------------------------------------------
    # 11E‑2 + 11E‑6 + 11E‑7: poll_once()
    # ------------------------------------------------------------
    def poll_once(self) -> Optional[Frame]:
        if not self.is_enabled():
            logger.info("polling_disabled_poll_once")
            return None

        frame = self.get_frame()

        if frame is None:
            logger.warning("poll_once_no_frame")
            self.frames_skipped += 1
            self.last_frame = None
            return None

        try:
            self.ingestion.ingest(frame)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "ingestion_error",
                extra={"frame": frame, "error": str(exc)},
            )
            self.frames_failed += 1
            self.last_frame = frame
            return None

        self.frames_ingested += 1
        self.last_frame = frame

        logger.debug("poll_once_success", extra={"frame": frame})
        return frame

    # ------------------------------------------------------------
    # 11E‑3 + 11E‑7: poll_forever()
    # ------------------------------------------------------------
    def poll_forever(self) -> None:
        if not self.is_enabled():
            logger.info("polling_disabled_poll_forever")
            return

        max_frames: int = int(self.config.get("MAX_FRAMES", 10))
        logger.debug("poll_forever_start", extra={"max_frames": max_frames})

        for _ in range(max_frames):
            self.poll_once()

        logger.debug("poll_forever_complete")

    # ------------------------------------------------------------
    # 11E‑6: Diagnostics surface
    # ------------------------------------------------------------
    def get_diagnostics(self) -> Dict[str, Any]:
        mode = "fake" if self.config.get("USE_FAKE_FRAMES", True) else "serial"

        diagnostics = {
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

        logger.debug("poller_diagnostics", extra=diagnostics)
        return diagnostics
