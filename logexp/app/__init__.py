# filename: logexp/app/__init__.py
# Canonical application factory for LogExp.
# Provides deterministic config layering, extension initialization,
# ingestion/analytics contracts, and structured logging behavior.

from __future__ import annotations

import datetime
import os
import sqlite3
import sys
from typing import Any, Dict, Optional, Tuple

from flask import current_app, render_template

from logexp.app.blueprints import register_blueprints
from logexp.app.config import load_config
from logexp.app.extensions import db, migrate
from logexp.app.logging_setup import configure_logging, get_logger
from logexp.app.middleware.request_id import request_id_middleware
from logexp.app.typing import LogExpFlask, LogExpRequest

logger = get_logger("logexp.app")


# ---------------------------------------------------------------------------
# SQLite timezone support
# ---------------------------------------------------------------------------


def configure_sqlite_timezone_support(app: LogExpFlask) -> None:
    """
    Ensures SQLite stores and returns timezone-aware datetimes.
    Must run AFTER config overrides but BEFORE db.init_app().
    """

    def adapt_datetime(dt: datetime.datetime) -> str:
        return dt.isoformat()

    def convert_datetime(val: Any) -> Optional[datetime.datetime]:
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
        "connect_args": {"detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES}
    }

    logger.debug("sqlite_timezone_support_enabled")


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------


def create_app(overrides: Optional[Dict[str, Any]] = None) -> LogExpFlask:
    """
    Central application factory.

    Contract:
      - Deterministic config layering
      - No side effects at import time
      - Extensions initialized in a stable, predictable order
      - Ingestion and analytics controlled by explicit config flags
    """

    logger.debug("app_factory_start")

    # Typed Flask subclass (declares config_obj and poller)
    app: LogExpFlask = LogExpFlask(__name__)

    # Typed Request subclass (declares request_id)
    app.request_class = LogExpRequest

    # 1. Load config (single source of truth)
    app.config_obj = load_config(overrides=overrides or {})
    app.config.update(app.config_obj)

    logger.debug(
        "config_loaded",
        extra={"keys": list(app.config_obj.keys())},
    )

    # ----------------------------------------------------------------------
    # DATABASE FALLBACK
    # ----------------------------------------------------------------------
    has_uri = bool(app.config.get("SQLALCHEMY_DATABASE_URI"))
    has_binds = bool(app.config.get("SQLALCHEMY_BINDS"))

    if not has_uri and not has_binds:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        logger.debug("database_fallback_applied", extra={"uri": "sqlite:///:memory:"})
    else:
        logger.debug(
            "database_config_present",
            extra={"has_uri": has_uri, "has_binds": has_binds},
        )

    # 2. SQLite timezone support
    configure_sqlite_timezone_support(app)

    # 3. Structured logging
    configure_logging()
    logger.debug("structured_logging_configured")

    # 3b. Request ID middleware (Step‑12C)
    request_id_middleware(app)
    logger.debug("request_id_middleware_enabled")

    # 4. Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    logger.debug("extensions_initialized")

    # 5. Register blueprints
    register_blueprints(app)
    logger.debug("blueprints_registered")

    # 6. Poller startup REMOVED — now handled in wsgi.py
    app.logger.info(
        "Poller startup moved to wsgi.py (START_POLLER, gunicorn, shell, tests respected)."
    )

    # ----------------------------------------------------------------------
    # 7. Error handlers
    # ----------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found_error(error: Exception) -> Tuple[str, int]:
        logger.debug("error_404_triggered")
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error: Exception) -> Tuple[str, int]:
        logger.debug("error_403_triggered")
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error: Exception) -> Tuple[str, int]:
        logger.error("error_500_triggered", extra={"error": str(error)})
        return render_template("errors/500.html"), 500

    # ----------------------------------------------------------------------
    # 8. Teardown: stop poller safely in tests
    # ----------------------------------------------------------------------

    @app.teardown_appcontext
    def shutdown_poller(exception: Optional[BaseException] = None) -> None:
        poller = getattr(app, "poller", None)
        if app.config_obj.get("TESTING", False) and poller is not None:
            try:
                poller.stop()
                logger.debug("poller_stopped_in_teardown")
            except RuntimeError:
                logger.debug("poller_stop_called_from_within_thread")

    # ----------------------------------------------------------------------
    # 9. CLI commands
    # ----------------------------------------------------------------------

    # mypy: Flask CLI decorators are untyped; we explicitly ignore the correct codes.
    @app.cli.command("geiger-start")  # type: ignore[no-untyped-call, untyped-decorator]
    def geiger_start() -> None:
        poller = getattr(current_app, "poller", None)
        if poller and not poller._thread.is_alive():
            poller.start()
            current_app.logger.info("Geiger poller started.")
        else:
            print("Poller already running.")

    @app.cli.command("geiger-stop")  # type: ignore[no-untyped-call, untyped-decorator]
    def geiger_stop() -> None:
        poller = getattr(current_app, "poller", None)
        if poller and poller._thread.is_alive():
            poller.stop()
            print("Geiger poller stopped.")
        else:
            print("Poller not running.")

    @app.cli.command("seed-data")  # type: ignore[no-untyped-call, untyped-decorator]
    def seed_data() -> None:
        from logexp.seeds import seed_data

        seed_data.run(app)
        current_app.logger.info("Database seeded (idempotent).")

    @app.cli.command("clear-db")  # type: ignore[no-untyped-call, untyped-decorator]
    def clear_db() -> None:
        with app.app_context():
            db.drop_all()
            db.create_all()
            current_app.logger.info("Test database cleared and recreated.")

    # ----------------------------------------------------------------------
    # 10. Startup Diagnostics Banner
    # ----------------------------------------------------------------------

    logger.info(
        "startup_diagnostics",
        extra={
            "cwd": os.getcwd(),
            "python": sys.executable,
            "version": sys.version,
            "filtered_env": {
                k: v
                for k, v in os.environ.items()
                if any(x in k for x in ["SQL", "FLASK", "PYTHON", "TZ", "ANALYTICS"])
            },
        },
    )

    logger.debug("app_factory_complete")

    return app


__all__ = ["db", "create_app"]
