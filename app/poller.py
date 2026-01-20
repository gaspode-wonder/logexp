# filename: logexp/app/poller.py

from __future__ import annotations

import os
import threading
import time
from typing import Any, Optional

from app.logging_setup import get_logger


class GeigerPoller:
    """
    Background thread that continuously reads from the Geiger counter,
    parses the data, and stores readings in the database.

    All heavy imports (ingestion, geiger, db) are intentionally lazy to avoid
    circular imports during app initialization.
    """

    def __init__(self, app: Any, interval: int = 5) -> None:
        self.app: Any = app
        self.interval: int = interval

        # Subsystem logger (Step‑12C)
        self.logger = get_logger("beamfoundry.poller")

        # Lifecycle state
        self._running: bool = False
        self._stopping: bool = False

        # Thread control
        self._stop_event: threading.Event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the poller thread if not already running."""

        # Test mode guard
        if self.app.config_obj.get("TESTING", False):
            self.logger.debug("Poller disabled in TESTING mode.")
            return

        # Gunicorn guard
        if "gunicorn" in os.environ.get("SERVER_SOFTWARE", "").lower():
            self.logger.info("Poller disabled under Gunicorn worker.")
            return

        # Docker build guard
        if os.environ.get("DOCKER_BUILD", "") == "1":
            self.logger.info("Poller disabled during Docker build.")
            return

        # Already running?
        if self._running:
            self.logger.warning("Poller.start() called but poller is already running.")
            return

        self._running = True
        self._stopping = False
        self._stop_event.clear()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        self.logger.info(
            "GeigerPoller starting",
            extra={
                "interval": self.app.config_obj["POLL_INTERVAL"],
                "device": self.app.config_obj["GEIGER_DEVICE_PATH"],
            },
        )

    # ------------------------------------------------------------------
    def stop(self) -> None:
        """Signal the poller thread to stop and wait for it to exit."""

        if not self._running:
            self.logger.warning("Poller.stop() called but poller is not running.")
            return

        if self._stopping:
            self.logger.debug("Poller.stop() called again; already stopping.")
            return

        self._stopping = True
        self._running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            if threading.current_thread() != self._thread:
                self._thread.join(timeout=2)
                self.logger.info("GeigerPoller stopped cleanly.")
            else:
                self.logger.debug("Poller.stop() called from poller thread; skipping join.")

    # ------------------------------------------------------------------
    def _run(self) -> None:
        """
        Main polling loop.

        Reads raw serial data, parses it, stores readings, and sleeps.
        Runs inside the Flask application context.

        Heavy imports are intentionally placed here to avoid circular imports.
        """
        with self.app.app_context():
            # Lazy imports to avoid circular dependencies
            from app.extensions import db
            from app.geiger import parse_geiger_line, read_geiger
            from app.ingestion import ingest_reading

            config: dict[str, Any] = self.app.config_obj

            while not self._stop_event.is_set():
                try:
                    port: str = config["GEIGER_DEVICE_PATH"]
                    baud: int = config["GEIGER_BAUDRATE"]
                    threshold: int = config["GEIGER_THRESHOLD"]

                    raw: str = read_geiger(port, baud)
                    parsed: dict[str, Any] = parse_geiger_line(raw, threshold=threshold)

                    ingest_reading(parsed)

                    self.logger.debug(
                        "Poller tick",
                        extra={
                            "cps": parsed["counts_per_second"],
                            "cpm": parsed["counts_per_minute"],
                            "microsieverts_per_hour": parsed["microsieverts_per_hour"],
                            "mode": parsed["mode"],
                        },
                    )

                except Exception as exc:
                    db.session.rollback()
                    self.logger.error(
                        "Geiger poll error",
                        extra={"error": str(exc)},
                    )

                time.sleep(config["POLL_INTERVAL"])
