# filename: logexp/app/cli.py

from __future__ import annotations

from flask import Flask, current_app

from app.extensions import db


def register_cli(app: Flask) -> None:
    @app.cli.command("geiger-start")
    def geiger_start() -> None:
        poller = getattr(current_app, "poller", None)
        if poller and not poller._thread.is_alive():
            poller.start()
            current_app.logger.info("Geiger poller started.")
        else:
            print("Poller already running.")

    @app.cli.command("geiger-stop")
    def geiger_stop() -> None:
        poller = getattr(current_app, "poller", None)
        if poller and poller._thread.is_alive():
            poller.stop()
            print("Geiger poller stopped.")
        else:
            print("Poller not running.")

    @app.cli.command("seed-data")
    def seed_data() -> None:
        from seeds import seed_data

        seed_data.run(app)
        current_app.logger.info("Database seeded (idempotent).")

    @app.cli.command("clear-db")
    def clear_db() -> None:
        with app.app_context():
            db.drop_all()
            db.create_all()
            current_app.logger.info("Test database cleared and recreated.")
