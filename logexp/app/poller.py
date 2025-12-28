from __future__ import annotations

import threading
import time
import os
from datetime import datetime, timezone
from typing import Optional

from flask import current_app

from logexp.app.geiger import read_geiger, parse_geiger_line
from logexp.app.extensions import db
from logexp.app.models import LogExpReading
from logexp.app.ingestion import ingest_reading


class GeigerPoller:
    """
    Background thread that continuously reads from the Geiger counter,
    parses the data, and stores readings in the database.

    Configuration is pulled from current_app.config_obj so changes to
    GEIGER_DEVICE_PATH, POLL_INTERVAL, or thresholds are always respected.
    """

    def __init__(self, app, interval: int = 5) -> None:
        self.app = app
        self.interval: int = interval

        # Lifecycle state
        self._running = False
        self._stopping = False

        # Thread control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the poller thread if not already running."""

        # Test mode guard
        if self.app.config_obj.get("TESTING", False):
            self.app.logger.debug("Poller disabled in TESTING mode.")
            return

        # Gunicorn guard
        if "gunicorn" in os.environ.get("SERVER_SOFTWARE", "").lower():
            self.app.logger.info("Poller disabled under Gunicorn worker.")
            return

        # Docker build guard
        if os.environ.get("DOCKER_BUILD", "") == "1":
            self.app.logger.info("Poller disabled during Docker build.")
            return

        # Already running?
        if self._running:
            self.app.logger.warning("Poller.start() called but poller is already running.")
            return

        self._running = True
        self._stopping = False
        self._stop_event.clear()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        self.app.logger.info(
            "GeigerPoller starting (interval=%s, device=%s)",
            self.app.config_obj["POLL_INTERVAL"],
            self.app.config_obj["GEIGER_DEVICE_PATH"],
        )

    # ------------------------------------------------------------------
    def stop(self) -> None:
        """Signal the poller thread to stop and wait for it to exit."""

        if not self._running:
            self.app.logger.warning("Poller.stop() called but poller is not running.")
            return

        if self._stopping:
            self.app.logger.debug("Poller.stop() called again; already stopping.")
            return

        self._stopping = True
        self._running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            if threading.current_thread() != self._thread:
                self._thread.join(timeout=2)
                self.app.logger.info("GeigerPoller stopped cleanly.")
            else:
                self.app.logger.debug("Poller.stop() called from poller thread; skipping join.")

    # ------------------------------------------------------------------
    def _run(self) -> None:
        """
        Main polling loop.

        Reads raw serial data, parses it, stores readings, and sleeps.
        Runs inside the Flask application context.
        """
        with self.app.app_context():
            config = self.app.config_obj

            while not self._stop_event.is_set():
                try:
                    port = config["GEIGER_DEVICE_PATH"]
                    baud = config["GEIGER_BAUDRATE"]
                    threshold = config["GEIGER_THRESHOLD"]

                    raw = read_geiger(port, baud)
                    parsed = parse_geiger_line(raw, threshold=threshold)

                    parsed = parse_geiger_line(raw, threshold=threshold)

                    ingest_reading(parsed)

                    self.app.logger.debug(
                        "Poller tick: cps=%s cpm=%s µSv/h=%s mode=%s",
                        parsed["counts_per_second"],
                        parsed["counts_per_minute"],
                        parsed["microsieverts_per_hour"],
                        parsed["mode"],
                    )

                except Exception as exc:
                    # ingestion.reading already rolls back on ingestion errors;
                    # this catch is for read/parse errors and any unexpected failures.
                    db.session.rollback()
                    self.app.logger.error(f"Geiger poll error: {exc}")

                time.sleep(config["POLL_INTERVAL"])