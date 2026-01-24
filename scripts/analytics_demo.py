# filename: scripts/analytics_demo.py

from __future__ import annotations

from beamfoundry.services.analytics_utils import summarize_readings


def main() -> int:
    """Run a small analytics demo to verify the analytics subsystem."""
    sample = [1.0, 2.0, 3.0, 4.0]

    summary = summarize_readings(sample)
    print("Analytics demo summary:")
    print(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
