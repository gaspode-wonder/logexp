DEFAULTS = {
    # Environment
    "LOGEXP_ENV": "development",
    "DATABASE_URL": "sqlite:///logexp.db",
    "TIMEZONE": "UTC",

    # Poller
    "START_POLLER": True,
    "POLL_INTERVAL": 5,  # seconds
    "GEIGER_DEVICE_PATH": "/dev/ttyUSB0",

    # Analytics
    "ANALYTICS_ENABLED": True,
    "ANALYTICS_WINDOW_SECONDS": 60,
    "ANALYTICS_SMOOTHING_FACTOR": 0.5,

    # Ingestion
    "INGESTION_ENABLED": True,
    "INGESTION_BATCH_SIZE": 100,

    # Database
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",

    # Testing
    "TESTING": False,

    # UI toggles
    "SHOW_DIAGNOSTICS": True,
    "SHOW_ANALYTICS": True,
}