#!/usr/bin/env python3

from logexp.app import create_app
from logexp.app.extensions import db
from logexp.app.config import TestConfig


def main() -> None:
    app = create_app(TestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()

    print("Test DB rebuilt.")


if __name__ == "__main__":
    main()
