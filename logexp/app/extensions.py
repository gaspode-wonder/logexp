# filename: logexp/app/extensions.py

from __future__ import annotations

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.extensions")


class Base(DeclarativeBase):
    pass


db: SQLAlchemy = SQLAlchemy(model_class=Base)
migrate: Migrate = Migrate()

logger.debug(
    "extensions_initialized",
    extra={"extensions": ["sqlalchemy", "migrate"]},
)
