# filename: logexp/app/extensions.py

from __future__ import annotations

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.extensions")

# SQLAlchemy and Migrate extensions used across the application.
db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

logger.debug(
    "extensions_initialized",
    extra={"extensions": ["sqlalchemy", "migrate"]},
)
