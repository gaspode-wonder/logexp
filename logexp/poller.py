# filename: logexp/poller.py

from __future__ import annotations

import serial
from typing import Any, Dict, Optional, Union

from logexp.app.logging_setup import get_logger
from logexp.poller_config import PollerConfig

logger = get_logger("logexp.poller")


class Poller:
    """
    Poller with unified configuration surface.

    Accepts either:
      - PollerConfig (preferred)
      - legacy dict config (compatibility layer)
    """

    def __init__(
        self,
        config: Union[PollerConfig, Dict[str, Any]],
        ingestion: Any,
    ) -> None:
        # Compatibility layer: allow old dict configs
        if isinstance(config, dict):
            self.config = self._from_legacy_dict(config)
        else:
            self.config = config

        self.ingestion = ingestion

        # Track successful ingestions separately from attempted frames
        self._successful_ingestions: int = 0

        logger.debug(
            "poller_initialized",
            extra={
                "mode": self.config.mode,
                "serial_port": self.config.serial_port,
                "polling_enabled": self.config.polling_enabled,
            },
        )

    # ----------------------------------------------------------------------
    # Compatibility: convert legacy dict config → PollerConfig
    # ----------------------------------------------------------------------
    def _from_legacy_dict(self, cfg: Dict[str, Any]) -> PollerConfig:
        use_fake = cfg.get("USE_FAKE_FRAMES", False)

        if use_fake:
            return PollerConfig(
                mode="fake",
                polling_enabled=cfg.get("POLLING_ENABLED", True),
                fake_frame_value=cfg.get("FAKE_FRAME_VALUE", 42),
                max_frames=cfg.get("MAX_FRAMES", 5),
            )

        return PollerConfig(
            mode="serial",
            polling_enabled=cfg.get("POLLING_ENABLED", True),
            serial_port=cfg.get("SERIAL_PORT"),
            serial_baudrate=cfg.get("SERIAL_BAUDRATE", 9600),
            serial_timeout=cfg.get("SERIAL_TIMEOUT", 1.0),
            max_frames=cfg.get("MAX_FRAMES", 5),
        )

    # ----------------------------------------------------------------------
    # Polling logic
    # ----------------------------------------------------------------------
    def poll_once(self) -> Optional[Dict[str, Any]]:
        """
        Poll a single frame according to the configured mode.

        - Respects polling_enabled: returns None if disabled.
        - In fake mode, always returns a deterministic frame.
        - In serial mode, returns None on errors or empty reads.
        """
        if not self.config.polling_enabled:
            logger.debug("poll_once_skipped_polling_disabled")
            return None

        if self.config.mode == "fake":
            return self._poll_fake()

        if self.config.mode == "serial":
            return self._poll_serial()

        # Defensive branch: unreachable in type space but valid at runtime.
        logger.error(  # type: ignore[unreachable]
            "unknown_poller_mode",
            extra={"mode": self.config.mode},
        )
        return None  # pragma: no cover

    def _poll_fake(self) -> Dict[str, Any]:
        frame = {"raw": str(self.config.fake_frame_value)}
        try:
            self.ingestion.ingest(frame)
            self._successful_ingestions += 1
        except Exception:
            logger.error("fake_ingestion_failure")
        return frame

    def _poll_serial(self) -> Optional[Dict[str, Any]]:
        if not self.config.serial_port:
            logger.error("serial_port_missing")
            return None

        try:
            with serial.Serial(
                self.config.serial_port,
                self.config.serial_baudrate,
                timeout=self.config.serial_timeout,
            ) as ser:
                raw = ser.readline().decode("utf-8").strip()
        except Exception:
            logger.error("serial_read_failure")
            return None

        if not raw:
            logger.warning("poll_once_no_frame")
            return None

        frame = {"raw": raw}
        try:
            self.ingestion.ingest(frame)
            self._successful_ingestions += 1
        except Exception:
            logger.error("serial_ingestion_failure")

        return frame

    def poll_forever(self) -> None:
        """
        Poll repeatedly until max_frames is reached or polling is disabled.

        - If polling_enabled is False: returns immediately.
        - If max_frames is None: loops forever (tests use finite bounds).
        """
        if not self.config.polling_enabled:
            logger.debug("poll_forever_skipped_polling_disabled")
            return

        max_frames = self.config.max_frames
        count = 0

        while True:
            _ = self.poll_once()
            count += 1

            if max_frames is not None and count >= max_frames:
                break

    # ----------------------------------------------------------------------
    # Diagnostics
    # ----------------------------------------------------------------------
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Minimal, JSON-safe diagnostics for the poller.

        - mode: "fake" or "serial"
        - polling_enabled: bool flag
        - frames_ingested: number of *successful* ingestions
        - serial: sub-section with port info when in serial mode
        """
        base: Dict[str, Any] = {
            "mode": self.config.mode,
            "polling_enabled": self.config.polling_enabled,
            "frames_ingested": self._successful_ingestions,
        }

        if self.config.mode == "serial":
            base["serial"] = {
                "port": self.config.serial_port,
                "baudrate": self.config.serial_baudrate,
                "timeout": self.config.serial_timeout,
            }

        return base
