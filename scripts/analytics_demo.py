# filename: scripts/analytics_demo.py

# """
# Run the analytics engine in an isolated test application context.
#
# Creates an app with TESTING=True and START_POLLER=False,
# executes run_analytics() against the database session,
# and prints the resulting analytics payload.
# """

from __future__ import annotations

from typing import Any, Dict

from logexp.app import create_app
from logexp.app.extensions import db
from logexp.app.services.analytics import run_analytics


def main() -> None:
    overrides: Dict[str, Any] = {
        "TESTING": True,
        "START_POLLER": False,
    }

    app = create_app(overrides)

    with app.app_context():
        result = run_analytics(db.session)

    print("Analytics demo complete:", result)


if __name__ == "__main__":
    main()
