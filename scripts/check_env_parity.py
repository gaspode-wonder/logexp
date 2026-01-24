# filename: scripts/check_env_parity.py

from __future__ import annotations

import os
import sys
from typing import List


def main() -> int:
    """Check for environment parity issues that commonly break CI."""
    problems: List[str] = []

    # Python version check
    if not sys.version.startswith("3.10"):
        problems.append(f"Python version mismatch: {sys.version}")

    # Virtual environment check
    if "VIRTUAL_ENV" not in os.environ:
        problems.append("VIRTUAL_ENV is not set")

    # Timezone check (used by CI-HARD)
    tz = os.environ.get("LOCAL_TIMEZONE")
    if tz not in {"UTC", None}:
        problems.append(f"Unexpected LOCAL_TIMEZONE: {tz}")

    if problems:
        print("Environment parity check failed:")
        for p in problems:
            print(f" - {p}")
        return 1

    print("Environment parity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
