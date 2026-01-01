# logexp/poller.py

import logging
from typing import Any, Dict, Optional

import serial

logger = logging.getLogger("logexp.poller")


class Poller:
    """
    Step 11E — Poller implementation.

    11E‑1: skeleton
    11E‑2: poll_once() (fake frame path)
    11E‑3: poll_forever() loop (deterministic, test‑safe)
    11E‑5: optional real serial reading via pyserial (still test‑safe)
    """

    def __init__(self, config: Dict[str, Any], ingestion: Any) -> None:
        """
        :param config: Configuration mapping (typically config_obj or a subset).
        :param ingestion: Ingestion facade with an 'ingest' method that accepts a frame dict.
        """
        self.config = config
        self.ingestion = ingestion

    # ------------------------------------------------------------
    # 11E‑5: Real serial frame provider (still test‑safe)
    # ------------------------------------------------------------
    def read_serial_frame(self) -> Optional[Dict[str, Any]]:
        """
        Read a single frame from the configured serial port.

        This method is:
        - lazy (opens the port per call)
        - patchable in tests (serial.Serial can be monkeypatched)
        - non‑raising (logs and returns None on error)
        - minimal parsing: returns {"raw": <line>}
        """
        port = self.config.get("SERIAL_PORT")
        baudrate = self.config.get("SERIAL_BAUDRATE", 9600)
        timeout = self.config.get("SERIAL_TIMEOUT", 1.0)

        if not port:
            logger.error("SERIAL_PORT not configured; cannot read frame from serial.")
            return None

        try:
            with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
                raw_bytes = ser.readline()
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
    # 11E‑2 + 11E‑5: Deterministic frame provider with fake/real switch
    # ------------------------------------------------------------
    def get_frame(self) -> Optional[Dict[str, Any]]:
        """
        Provide a single frame for ingestion.

        Behavior:
        - If USE_FAKE_FRAMES is True or unset:
            -> return deterministic fake frame.
        - If USE_FAKE_FRAMES is False:
            -> attempt to read from serial.
        """
        use_fake = self.config.get("USE_FAKE_FRAMES", True)

        if use_fake:
            fake_value = self.config.get("FAKE_FRAME_VALUE", 42)
            return {"value": fake_value}

        return self.read_serial_frame()

    # ------------------------------------------------------------
    # 11E‑2: poll_once()
    # ------------------------------------------------------------
    def poll_once(self) -> Optional[Dict[str, Any]]:
        """
        Perform a single poll operation.

        Steps:
        - Obtain a frame via get_frame().
        - If None, log and return None.
        - Otherwise, hand the frame to ingestion.ingest(frame).
        """
        frame = self.get_frame()

        if frame is None:
            logger.warning("poll_once() obtained no frame; skipping ingestion.")
            return None

        try:
            self.ingestion.ingest(frame)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error during ingestion of frame %r: %s", frame, exc)
            return None

        return frame

    # ------------------------------------------------------------
    # 11E‑3: poll_forever()
    # ------------------------------------------------------------
    def poll_forever(self) -> None:
        """
        Loop around poll_once() a finite number of times.

        Deterministic and test‑safe:
        - No threads
        - No daemon behavior
        - No infinite loops
        """
        max_frames = self.config.get("MAX_FRAMES", 10)

        for _ in range(max_frames):
            self.poll_once()
