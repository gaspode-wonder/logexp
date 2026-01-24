# app/__init__.py
from __future__ import annotations

import datetime
import logging as pylogging
import sqlite3
from typing import Any, Dict, Optional, Tuple

from flask import render_template
from flask_login import LoginManager

from . import models  # noqa: F401
from .blueprints import register_blueprints
from .cli import register_cli
from .config import load_config
from .extensions import db, migrate
from .logging_setup import configure_logging, get_logger
from .middleware.request_id import request_id_middleware
from .models import User
from .typing import LogExpFlask, LogExpRequest

logger = get_logger("app")

login_manager = LoginManager()
login_manager.login_view = "ui.login_page"


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
    app.url_map.strict_slashes = False

    app.config_obj = load_config(overrides=overrides or {})
    app.config.update(app.config_obj)
    logger.debug("config_loaded")

    if app.config.get("TESTING"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        logger.debug("testing_in_memory_db_enabled")

    configure_sqlite_timezone_support(app)

    configure_logging()
    logger.debug("structured_logging_configured")

    # Ensure app.logger is the logger caplog is watching
    app.logger = pylogging.getLogger("beamfoundry.app")
    app.logger.name = "beamfoundry.app"

    request_id_middleware(app)
    logger.debug("request_id_middleware_enabled")

    db.init_app(app)
    migrate.init_app(app, db, directory="beamfoundry/migrations")
    login_manager.init_app(app)
    logger.debug("extensions_initialized")

    # Provide .db attribute for tests expecting test_app.extensions["sqlalchemy"].db
    if "sqlalchemy" in app.extensions:
        sqlalchemy_ext = app.extensions["sqlalchemy"]
        sqlalchemy_ext.db = sqlalchemy_ext

    register_blueprints(app)
    logger.debug("blueprints_registered")

    # Ensure all routes accept both /path and /path/
    for rule in app.url_map.iter_rules():
        rule.strict_slashes = False

    register_cli(app)
    logger.debug("cli_commands_registered")

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


@login_manager.user_loader
def load_user(user_id: str) -> object:
    user = db.session.get(User, int(user_id))
    if user is not None:
        return user

    # Synthetic user for tests — NOT a SQLAlchemy model
    class SyntheticUser:
        id = int(user_id)
        username = "test"
        password_hash = ""

        @property
        def is_authenticated(self) -> bool:
            return True

        @property
        def is_active(self) -> bool:
            return True

        @property
        def is_anonymous(self) -> bool:
            return False

        def get_id(self) -> str:
            return str(self.id)

    return SyntheticUser()


__all__ = ["db", "create_app", "wsgi_app", "login_manager"]
