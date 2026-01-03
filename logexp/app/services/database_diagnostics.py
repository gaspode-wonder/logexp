# filename: logexp/app/services/database_diagnostics.py

from __future__ import annotations

from typing import Optional

from flask import current_app
from sqlalchemy import text

from logexp.app.logging_setup import get_logger
from logexp.analytics.diagnostics import get_database_status as pure_db_status
from logexp.app.extensions import db
from logexp.app.models import LogExpReading

logger = get_logger("logexp.database")


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

    logger.debug(
        "db_diag_start",
        extra={"uri": uri, "engine": engine},
    )

    # ------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------
    try:
        db.session.execute(text("SELECT 1"))
        connected: bool = True
        logger.debug("db_diag_connection_ok")
    except Exception as exc:
        connected = False
        logger.error(
            "db_diag_connection_failed",
            extra={"error": str(exc)},
        )

    # ------------------------------------------------------------
    # Readings count + last reading timestamp
    # ------------------------------------------------------------
    try:
        readings_count: Optional[int] = db.session.query(LogExpReading).count()
        last_row: Optional[LogExpReading] = (
            db.session.query(LogExpReading)
            .order_by(LogExpReading.timestamp.desc())
            .first()
        )
        last_reading_at = last_row.timestamp if last_row else None

        logger.debug(
            "db_diag_readings_ok",
            extra={
                "readings_count": readings_count,
                "last_reading_at": (
                    last_reading_at.isoformat() if last_reading_at else None
                ),
            },
        )
    except Exception as exc:
        readings_count = None
        last_reading_at = None
        logger.error(
            "db_diag_readings_failed",
            extra={"error": str(exc)},
        )

    # ------------------------------------------------------------
    # Alembic migration revision
    # ------------------------------------------------------------
    try:
        migration_revision: Optional[str] = db.session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar()

        logger.debug(
            "db_diag_migration_ok",
            extra={"migration_revision": migration_revision},
        )
    except Exception as exc:
        migration_revision = None
        logger.error(
            "db_diag_migration_failed",
            extra={"error": str(exc)},
        )

    # ------------------------------------------------------------
    # Schema check
    # ------------------------------------------------------------
    try:
        table_name: str = LogExpReading.__tablename__
        db.session.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
        schema_ok: bool = True

        logger.debug(
            "db_diag_schema_ok",
            extra={"table": table_name},
        )
    except Exception as exc:
        schema_ok = False
        logger.error(
            "db_diag_schema_failed",
            extra={"error": str(exc)},
        )

    # ------------------------------------------------------------
    # Delegate to pure diagnostics
    # ------------------------------------------------------------
    payload = pure_db_status(
        uri=uri,
        engine=engine,
        connected=connected,
        readings_count=readings_count,
        last_reading_at=last_reading_at,
        migration_revision=migration_revision,
        schema_ok=schema_ok,
    )

    logger.debug(
        "db_diag_complete",
        extra={"payload": payload},
    )

    return payload
