import threading, time
from logexp.app.geiger import read_geiger, parse_geiger_line

class GeigerPoller:
    def __init__(self, app, interval=5):
        self.app = app
        self.port = app.config["GEIGER_PORT"]
        self.baudrate = app.config["GEIGER_BAUDRATE"]
        self.threshold = app.config["GEIGER_THRESHOLD"]
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._stop_event.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        # Only join if called from a different thread
        if self._thread.is_alive() and threading.current_thread() != self._thread:
            self._thread.join()

    def _run(self):
        from logexp.app import db
        from logexp.app.models import LogExpReading
        with self.app.app_context():
            while not self._stop_event.is_set():
                try:
                    raw = read_geiger(self.port, self.baudrate)
                    parsed = parse_geiger_line(raw, threshold=self.threshold)
                    reading = LogExpReading(
                        counts_per_second=parsed["counts_per_second"],
                        counts_per_minute=parsed["counts_per_minute"],
                        microsieverts_per_hour=parsed["microsieverts_per_hour"],
                        mode=parsed["mode"]
                    )
                    db.session.add(reading)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    self.app.logger.error(f"Geiger poll error: {e}")
                time.sleep(self.interval)
