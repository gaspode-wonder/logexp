import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # ✅ Centralized Geiger settings
    GEIGER_PORT = os.environ.get("GEIGER_PORT", "/dev/tty.usbserial-AB9R9IYS")
    GEIGER_BAUDRATE = int(os.environ.get("GEIGER_BAUDRATE", "9600"))
    GEIGER_THRESHOLD = int(os.environ.get("GEIGER_THRESHOLD", "50"))

    # ✅ Local timezone for display formatting
    LOCAL_TIMEZONE = os.getenv("LOCAL_TIMEZONE", "America/Chicago")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOCAL_TIMEZONE = "US/Central"
    START_POLLER = False   # <-- critical: don’t start poller in tests

