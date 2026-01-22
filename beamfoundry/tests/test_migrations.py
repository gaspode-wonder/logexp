# tests/test_migrations.py

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_migrations_apply_cleanly(tmp_path: Path) -> None:
    """
    Apply database migrations against a temporary SQLite database.
    This is a fast signal that migration scripts are syntactically and
    structurally valid before running them against Postgres in CI.
    """
    db_path = tmp_path / "test.db"
    os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    os.environ.setdefault("LOCAL_TIMEZONE", "UTC")
    os.environ.setdefault("GEIGER_THRESHOLD", "0.1")
    os.environ.setdefault("START_POLLER", "False")

    # Use the same CLI path you use in real life
    completed = subprocess.run(
        ["flask", "--app", "beamfoundry_app", "db", "upgrade"],
        check=False,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        pytest.fail(
            f"flask db upgrade failed:\n"
            f"STDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}"
        )
