# filename: scripts/rebuild_test_db.py

#!/usr/bin/env python3

# """
# Rebuild the LogExp test database schema.
#
# Creates an application with TESTING=True and START_POLLER=False,
# drops all tables, recreates them, and exits cleanly.
# """

from __future__ import annotations

from typing import Any, Dict

from logexp.app import create_app
from logexp.app.extensions import db


def main() -> None:
    overrides: Dict[str, Any] = {
        "TESTING": True,
        "START_POLLER": False,
    }

    app = create_app(overrides)

    with app.app_context():
        db.drop_all()
        db.create_all()

    print("Test DB rebuilt.")


if __name__ == "__main__":
    main()
