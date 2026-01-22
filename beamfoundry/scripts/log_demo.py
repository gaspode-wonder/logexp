# filename: scripts/log_demo.py

# """
# Minimal logging demo for LogExp.
#
# Creates an application with TESTING=True and START_POLLER=False
# and emits a single structured log line.
# """

from __future__ import annotations

from typing import Any, Dict

from app import create_app


def main() -> None:
    overrides: Dict[str, Any] = {
        "TESTING": True,
        "START_POLLER": False,
    }

    app = create_app(overrides)
    app.logger.info("demo log line")


if __name__ == "__main__":
    main()
