#!/usr/bin/env python3

from logexp.app import create_app
from logexp.app.extensions import db


def main() -> None:
    app = create_app(
        {
            "TESTING": True,
            "START_POLLER": False,
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    print("Test DB rebuilt.")


if __name__ == "__main__":
    main()
