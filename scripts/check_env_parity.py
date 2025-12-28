#!/usr/bin/env python3
import os
import sys

REQUIRED_ENV_VARS = [
    "ANALYTICS_ENABLED",
    "ANALYTICS_WINDOW",
    "LOCAL_TIMEZONE",
]

missing = [var for var in REQUIRED_ENV_VARS if var not in os.environ]

if missing:
    print("Missing required environment variables:")
    for var in missing:
        print(f"  - {var}")
    sys.exit(1)

print("Environment parity check passed.")
