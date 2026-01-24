# filename: scripts/ci_diagnostics.py

from __future__ import annotations

import importlib


def main() -> int:
    """Verify that the beamfoundry package imports cleanly."""
    try:
        importlib.import_module("beamfoundry")
    except Exception as exc:
        print("Failed to import beamfoundry:")
        print(exc)
        return 1

    print("beamfoundry import OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
