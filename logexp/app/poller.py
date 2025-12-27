from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Optional

from flask import current_app

from logexp.app.geiger import read_geiger, parse_geiger_line
from logexp.app.extensions import db
from logexp.app.models import LogExpReading


class GeigerPoller:
    """
    Background thread that continuously reads from the Geiger counter,
    parses the data, and stores readings in the database.

    Configuration is pulled from current_app.config so changes to
    GEIGER_PORT, GEIGER_BAUDRATE, or GEIGER_THRESHOLD are always respected.
    """

    def __init__(self, app, interval: int = 5) -> None:
        self.app = app
        self.interval: int = interval

        # Thread control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the poller thread if not already running."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.app.logger.info("GeigerPoller started")

    # ------------------------------------------------------------------
    def stop(self) -> None:
        """Signal the poller thread to stop and wait for it to exit."""
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            if threading.current_thread() != self._thread:
                self._thread.join()
                self.app.logger.info("GeigerPoller stopped")

    # ------------------------------------------------------------------
    def _run(self) -> None:
        """
        Main polling loop.

        Reads raw serial data, parses it, stores readings, and sleeps.
        Runs inside the Flask application context.
        """
        with self.app.app_context():
            while not self._stop_event.is_set():
                try:
                    # Pull config dynamically so changes take effect immediately
                    port = current_app.config["GEIGER_PORT"]
                    baud = current_app.config["GEIGER_BAUDRATE"]
                    threshold = current_app.config["GEIGER_THRESHOLD"]

                    raw = read_geiger(port, baud)
                    parsed = parse_geiger_line(raw, threshold=threshold)

                    reading = LogExpReading(
                        timestamp=datetime.now().astimezone(timezone.utc),
                        counts_per_second=parsed["counts_per_second"],
                        counts_per_minute=parsed["counts_per_minute"],
                        microsieverts_per_hour=parsed["microsieverts_per_hour"],
                        mode=parsed["mode"],
                    )

                    db.session.add(reading)
                    db.session.commit()

                except Exception as exc:
                    db.session.rollback()
                    self.app.logger.error(f"Geiger poll error: {exc}")

                time.sleep(self.interval)