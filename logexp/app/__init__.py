# filename: logexp/app/__init__.py
# Canonical application factory for LogExp.
# Restores deterministic config layering, extension initialization,
# ingestion contract, analytics contract, and structured logging behavior.

from __future__ import annotations

import datetime
import sqlite3

from flask import Flask, current_app, render_template

from logexp.app.blueprints import register_blueprints
from logexp.app.config import load_config
from logexp.app.extensions import db, migrate
from logexp.app.logging_setup import configure_logging

# NOTE: Poller import removed to avoid circular imports.
# Poller is now started in wsgi.py.


# ---------------------------------------------------------------------------
# SQLite timezone support
# ---------------------------------------------------------------------------
def configure_sqlite_timezone_support(app: Flask) -> None:
    """
    Ensures SQLite stores and returns timezone-aware datetimes.
    Must run AFTER config overrides but BEFORE db.init_app().
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


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------
def create_app(overrides: dict | None = None) -> Flask:
    """
    Central application factory.

    Contract:
    - Deterministic config layering
    - No side effects at import time
    - Extensions initialized in a stable, predictable order
    - Ingestion and analytics controlled by explicit config flags
    """

    app = Flask(__name__)

    # 1. Load config
    app.config_obj = load_config(overrides=overrides or {})
    app.config.update(app.config_obj)
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config_obj["SQLALCHEMY_DATABASE_URI"]

    # 2. SQLite timezone support
    configure_sqlite_timezone_support(app)

    # 3. Structured logging
    configure_logging()

    # 4. Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 5. Register blueprints
    register_blueprints(app)

    # DEBUG: inspoect registered routes
    print(app.url_map)

    # 6. Poller startup REMOVED — now handled in wsgi.py
    app.logger.info(
        "Poller startup moved to wsgi.py (START_POLLER, gunicorn, shell, tests respected)."
    )

    # 7. Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    # 8. Teardown: stop poller safely in tests
    @app.teardown_appcontext
    def shutdown_poller(exception=None):
        if app.config_obj["TESTING"] and getattr(app, "poller", None):
            try:
                app.poller.stop()
            except RuntimeError:
                app.logger.debug(
                    "Poller stop called from within poller thread; skipping join."
                )

    # 9. CLI commands
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
