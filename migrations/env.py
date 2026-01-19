# filename: migrations/env.py

from __future__ import annotations

from alembic import context
from app.extensions import db

# Alembic Config object
config = context.config

# Disable Alembic’s logging configuration — Flask handles logging.
# (We intentionally do NOT call fileConfig here.)

# Use Flask‑Migrate’s metadata
target_metadata = db.Model.metadata


def run_migrations_online() -> None:
    from flask import current_app

    # Always use Flask’s engine — never alembic.ini
    connectable = current_app.extensions["migrate"].db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Flask‑Migrate does not support offline mode; always run online.
run_migrations_online()
