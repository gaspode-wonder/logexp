# filename: scripts/log_demo.py

from __future__ import annotations

from beamfoundry.logging_setup import get_logger


def main() -> int:
    """Emit a few demo log messages to verify logging configuration."""
    logger = get_logger("beamfoundry.demo")

    logger.debug("Demo debug message")
    logger.info("Demo info message")
    logger.warning("Demo warning message")
    logger.error("Demo error message")

    print("Log demo complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
