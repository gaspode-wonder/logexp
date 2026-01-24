# filename: scripts/rebuild_test_db.py

from __future__ import annotations

import os

from flask import Flask

from beamfoundry import create_app


def main() -> int:
    """Rebuild the test database from scratch."""
    db_path = "ci.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    app: Flask = create_app()
    with app.app_context():
        from flask_migrate import upgrade

        upgrade()

    print("Test DB rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
