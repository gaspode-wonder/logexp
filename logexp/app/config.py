import os
from typing import Optional


class Config:
    """
    Base configuration for LogExp.

    All environment-driven settings are centralized here so the application
    factory, poller, and blueprints can rely on a single source of truth.
    """

    # --- Database ---
    SQLALCHEMY_DATABASE_URI: Optional[str] = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # --- Security ---
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev")

    # --- Geiger / Poller Settings ---
    GEIGER_PORT: str = os.environ.get("GEIGER_PORT", "/dev/tty.usbserial-AB9R9IYS")
    GEIGER_BAUDRATE: int = int(os.environ.get("GEIGER_BAUDRATE", "9600"))
    GEIGER_THRESHOLD: int = int(os.environ.get("GEIGER_THRESHOLD", "50"))

    # --- Timezone ---
    LOCAL_TIMEZONE: str = os.environ.get("LOCAL_TIMEZONE", "America/Chicago")

    # --- Poller Control ---
    START_POLLER: bool = os.environ.get("START_POLLER", "False") == "True"


class TestConfig(Config):
    """
    Configuration used during pytest runs.

    Ensures:
    - No hardware poller starts
    - In-memory SQLite DB for speed
    - Stable timezone for deterministic tests
    """

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    LOCAL_TIMEZONE: str = "America/Chicago"
    START_POLLER: bool = False
