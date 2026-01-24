#!/usr/bin/env python3

# filename: scripts/check_env_parity.py

# """
# Check for required environment variables needed for analytics parity.
#
# This script is used by CI and local developers to ensure that
# critical analytics-related environment variables are present.
# """

from __future__ import annotations

import os
import sys
from typing import List

REQUIRED_ENV_VARS: List[str] = [
    "ANALYTICS_ENABLED",
    "ANALYTICS_WINDOW_SECONDS",
    "LOCAL_TIMEZONE",
]


def main() -> None:
    missing = [var for var in REQUIRED_ENV_VARS if var not in os.environ]

    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        sys.exit(1)

    print("Environment parity check passed.")


if __name__ == "__main__":
    main()
