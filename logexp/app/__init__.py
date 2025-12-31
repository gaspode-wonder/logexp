# logexp/app/__init__.py

from __future__ import annotations

import datetime
import os
import sqlite3

from flask import Flask, current_app, render_template

from logexp.app.blueprints import register_blueprints
from logexp.app.config import load_config
from logexp.app.extensions import db, migrate
from logexp.app.logging_loader import configure_logging
from logexp.app.poller import GeigerPoller


def configure_sqlite_timezone_support(app: Flask) -> None:
    """
    Ensures SQLite stores and returns timezone-aware datetimes.
    Must run AFTER config overrides but BEFORE db.init_app().
    """

    def adapt_datetime(dt: datetime.datetime) -> str:
        return dt.isoformat()

    def convert_datetime(val):
        # SQLite may give us:
        # - bytes (ISO string)
        # - str (ISO string)
        # - datetime (already parsed)
        # - None
        if val is None:
            return None

        if isinstance(val, datetime.datetime):
            return val

        if isinstance(val, bytes):
            val = val.decode()

        if isinstance(val, str):
            return datetime.datetime.fromisoformat(val)

        raise TypeError(f"Unexpected type for datetime conversion: {type(val)}")

    sqlite3.register_adapter(datetime.datetime, adapt_datetime)
    sqlite3.register_converter("timestamp", convert_datetime)

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        }
    }


def create_app(overrides: dict | None = None) -> Flask:
    """
    Central application factory.
    Accepts overrides so tests/dev/prod all use the same initialization path.
    """

    app = Flask(__name__)

    # Load config with optional overrides
    app.config_obj = load_config(overrides=overrides or {})

    # Apply DB URI to Flask config BEFORE initializing SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config_obj["SQLALCHEMY_DATABASE_URI"]

    # Apply SQLite timezone support BEFORE db.init_app()
    configure_sqlite_timezone_support(app)

    # Logging
    configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    register_blueprints(app)

    # Poller logic (disabled in tests)
    start_poller = app.config_obj["START_POLLER"]
    running_under_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "").lower()
    running_shell = os.environ.get("FLASK_SHELL", "").lower() in ("1", "true", "yes")
    running_tests = app.config_obj.get("TESTING", False)

    if (
        start_poller
        and not running_under_gunicorn
        and not running_shell
        and not running_tests
    ):
        app.logger.info("Starting GeigerPoller (safe mode).")
        app.poller = GeigerPoller(app)
        app.poller.start()
    else:
        app.logger.info(
            "Poller disabled (START_POLLER=False, running under Gunicorn, shell, or tests)."
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    # Teardown
    @app.teardown_appcontext
    def shutdown_poller(exception=None):
        if app.config_obj["TESTING"] and getattr(app, "poller", None):
            try:
                app.poller.stop()
            except RuntimeError:
                app.logger.debug(
                    "Poller stop called from within poller thread; skipping join."
                )

    # CLI commands
    @app.cli.command("geiger-start")
    def geiger_start():
        poller = getattr(current_app, "poller", None)
        if poller and not poller._thread.is_alive():
            poller.start()
            current_app.logger.info("Geiger poller started.")
        else:
            print("Poller already running.")

    @app.cli.command("geiger-stop")
    def geiger_stop():
        poller = getattr(current_app, "poller", None)
        if poller and poller._thread.is_alive():
            poller.stop()
            print("Geiger poller stopped.")
        else:
            print("Poller not running.")

    @app.cli.command("seed-data")
    def seed_data():
        from logexp.seeds import seed_data

        seed_data.run(app)
        current_app.logger.info("Database seeded (idempotent).")

    @app.cli.command("clear-db")
    def clear_db():
        with app.app_context():
            db.drop_all()
            db.create_all()
            current_app.logger.info("Test database cleared and recreated.")

    return app
