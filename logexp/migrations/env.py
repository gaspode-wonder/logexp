# filename: migrations/env.py
# Canonical Alembic environment for LogExp.
# Ensures Alembic always uses the exact same database URL and engine options
# that Flask resolves via load_config(), eliminating path drift and ambiguity.

import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

# ---------------------------------------------------------------------------
# Alembic Config
# ---------------------------------------------------------------------------

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# ---------------------------------------------------------------------------
# Force Alembic to use Flask’s resolved database URI
# ---------------------------------------------------------------------------

db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
config.set_main_option("sqlalchemy.url", db_uri)

# Flask-SQLAlchemy database object
target_db = current_app.extensions["migrate"].db

# ---------------------------------------------------------------------------
# Metadata for autogenerate
# ---------------------------------------------------------------------------


def get_metadata():
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata


# ---------------------------------------------------------------------------
# Offline Migrations
# ---------------------------------------------------------------------------


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online Migrations
# ---------------------------------------------------------------------------


def run_migrations_online():
    """Run migrations in 'online' mode."""

    # Prevent empty autogenerate revisions
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    conf_args = current_app.extensions["migrate"].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    # Use Flask’s engine directly — no guessing, no fallback
    engine = target_db.get_engine()

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
