# filename: scripts/rebuild_test_db.py

from __future__ import annotations

from typing import Any, Dict

from flask_migrate import upgrade

from app import create_app
from app.extensions import db


def main() -> None:
    overrides: Dict[str, Any] = {
        "TESTING": True,
        "START_POLLER": False,
    }

    app = create_app(overrides)

    with app.app_context():
        db.drop_all()
        upgrade()

    print("Test DB rebuilt via migrations.")


if __name__ == "__main__":
    main()
