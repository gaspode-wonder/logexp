# filename: logexp/app/services/database_diagnostics.py

from __future__ import annotations

from typing import Any, Optional

from flask import current_app
from sqlalchemy import text

from logexp.analytics.diagnostics import get_database_status as pure_db_status
from logexp.app.extensions import db
from logexp.app.models import Reading


def get_database_status() -> dict:
    """
    Flask-aware database diagnostics.

    Performs:
        - connection test
        - readings count
        - last reading timestamp
        - alembic migration revision lookup
        - schema check

    Delegates final formatting to the pure diagnostics function.
    """
    config = current_app.config_obj
    uri: str = config["SQLALCHEMY_DATABASE_URI"]
    engine: str = db.engine.name

    # ------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------
    try:
        db.session.execute(text("SELECT 1"))
        connected: bool = True
    except Exception:
        connected = False

    # ------------------------------------------------------------
    # Readings count + last reading timestamp
    # ------------------------------------------------------------
    try:
        readings_count: Optional[int] = db.session.query(Reading).count()
        last_row: Optional[Reading] = (
            db.session.query(Reading).order_by(Reading.timestamp.desc()).first()
        )
        last_reading_at = last_row.timestamp if last_row else None
    except Exception:
        readings_count = None
        last_reading_at = None

    # ------------------------------------------------------------
    # Alembic migration revision
    # ------------------------------------------------------------
    try:
        migration_revision: Optional[str] = db.session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar()
    except Exception:
        migration_revision = None

    # ------------------------------------------------------------
    # Schema check
    # ------------------------------------------------------------
    try:
        table_name: str = Reading.__tablename__
        db.session.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
        schema_ok: bool = True
    except Exception:
        schema_ok = False

    # ------------------------------------------------------------
    # Delegate to pure diagnostics
    # ------------------------------------------------------------
    return pure_db_status(
        uri=uri,
        engine=engine,
        connected=connected,
        readings_count=readings_count,
        last_reading_at=last_reading_at,
        migration_revision=migration_revision,
        schema_ok=schema_ok,
    )
