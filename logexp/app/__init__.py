# logexp/app/__init__.py

from __future__ import annotations

import os
import sqlite3
import datetime
from flask import Flask, render_template, current_app

from logexp.app.config import load_config
from logexp.app.poller import GeigerPoller
from logexp.app.extensions import db, migrate
from logexp.app.blueprints import register_blueprints
from logexp.app.logging_loader import configure_logging


def configure_sqlite_timezone_support(app: Flask) -> None:
    """
    Ensures SQLite stores and returns timezone-aware datetimes.
    Must run BEFORE db.init_app().
    """

    def adapt_datetime(dt: datetime.datetime) -> str:
        return dt.isoformat()

    def convert_datetime(val):
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
    Deterministic, layered, test‑friendly initialization.
    """

    app = Flask(__name__)
    # ------------------------------------------------------------------
    # 1. Load layered config (defaults → env → overrides)
    # ------------------------------------------------------------------
    config_obj = load_config(overrides=overrides or {})
    app.config_obj = config_obj
    app.config.update(config_obj)

    # ------------------------------------------------------------------
    # 2. SQLite timezone support BEFORE db.init_app()
    # ------------------------------------------------------------------
    configure_sqlite_timezone_support(app)

    # ------------------------------------------------------------------
    # 3. Logging AFTER config is applied
    # ------------------------------------------------------------------
    configure_logging(app)

    # ------------------------------------------------------------------
    # 4. Initialize extensions inside app context
    # ------------------------------------------------------------------
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)

    # ------------------------------------------------------------------
    # 5. Register blueprints
    # ------------------------------------------------------------------
    register_blueprints(app)

    # ------------------------------------------------------------------
    # 6. Poller logic (disabled in tests)
    # ------------------------------------------------------------------
    start_poller = config_obj["START_POLLER"]
    running_under_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "").lower()
    running_shell = os.environ.get("FLASK_SHELL", "").lower() in ("1", "true", "yes")
    running_tests = config_obj.get("TESTING", False)

    if start_poller and not running_under_gunicorn and not running_shell and not running_tests:
        app.logger.info("Starting GeigerPoller (safe mode).")
        app.poller = GeigerPoller(app)
        app.poller.start()
    else:
        app.logger.info(
            "Poller disabled (START_POLLER=False, running under Gunicorn, shell, or tests)."
        )

    # ------------------------------------------------------------------
    # 7. Error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    # ------------------------------------------------------------------
    # 8. Teardown: stop poller in tests
    # ------------------------------------------------------------------
    @app.teardown_appcontext
    def shutdown_poller(exception=None):
        if config_obj["TESTING"] and getattr(app, "poller", None):
            try:
                app.poller.stop()
            except RuntimeError:
                app.logger.debug(
                    "Poller stop called from within poller thread; skipping join."
                )

    # ------------------------------------------------------------------
    # 9. CLI commands
    # ------------------------------------------------------------------
    @app.cli.command("geiger-start")
    def geiger_start():
        poller = getattr(current_app, "poller", None)
        if poller and not poller._thread.is_alive():
            poller.start()
            current_app.logger.info("Geiger poller started.")
        else:
            app.logger.debug("Poller already running.")

    @app.cli.command("geiger-stop")
    def geiger_stop():
        poller = getattr(current_app, "poller", None)
        if poller and poller._thread.is_alive():
            poller.stop()
            app.logger.debug("Geiger poller stopped.")
        else:
            app.logger.debug("Poller not running.")

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
