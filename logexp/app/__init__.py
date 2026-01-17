# filename: logexp/app/__init__.py

from __future__ import annotations

import datetime
import sqlite3
from typing import Any, Dict, Optional, Tuple

from flask import render_template

from logexp.app import models  # noqa: F401
from logexp.app.blueprints import register_blueprints
from logexp.app.cli import register_cli
from logexp.app.config import load_config
from logexp.app.extensions import db, migrate
from logexp.app.logging_setup import configure_logging, get_logger
from logexp.app.middleware.request_id import request_id_middleware
from logexp.app.typing import LogExpFlask, LogExpRequest

logger = get_logger("logexp.app")


def configure_sqlite_timezone_support(app: LogExpFlask) -> None:
    def adapt_datetime(dt: datetime.datetime) -> str:
        return dt.isoformat()

    def convert_datetime(val: Any) -> Optional[datetime.datetime]:
        if val is None:
            return None
        if isinstance(val, bytes):
            val = val.decode()
        return datetime.datetime.fromisoformat(val)

    sqlite3.register_adapter(datetime.datetime, adapt_datetime)
    sqlite3.register_converter("timestamp", convert_datetime)
    logger.debug("sqlite_timezone_support_enabled")


def create_app(overrides: Optional[Dict[str, Any]] = None) -> LogExpFlask:
    logger.debug("app_factory_start")

    app: LogExpFlask = LogExpFlask(__name__)
    app.request_class = LogExpRequest

    # 1. Load config
    app.config_obj = load_config(overrides=overrides or {})
    app.config.update(app.config_obj)
    logger.debug("config_loaded")

    # 2. SQLite timezone support
    configure_sqlite_timezone_support(app)

    # 3. Structured logging
    configure_logging()
    logger.debug("structured_logging_configured")

    # 4. Request ID middleware
    request_id_middleware(app)
    logger.debug("request_id_middleware_enabled")

    # 5. Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, directory="logexp/migrations")
    logger.debug("extensions_initialized")

    # 6. Register blueprints
    register_blueprints(app)
    logger.debug("blueprints_registered")

    # 7. Register CLI
    register_cli(app)
    logger.debug("cli_commands_registered")

    # 8. Error handlers
    @app.errorhandler(404)
    def not_found_error(error: Exception) -> Tuple[str, int]:
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error: Exception) -> Tuple[str, int]:
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error: Exception) -> Tuple[str, int]:
        logger.error("error_500_triggered", extra={"error": str(error)})
        return render_template("errors/500.html"), 500

    logger.debug("app_factory_complete")
    return app


def wsgi_app() -> LogExpFlask:
    return create_app()


__all__ = ["db", "create_app", "wsgi_app"]
