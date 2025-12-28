import os

def coerce_value(key, value):
    if key in {"START_POLLER", "ANALYTICS_ENABLED", "INGESTION_ENABLED",
               "SHOW_DIAGNOSTICS", "SHOW_ANALYTICS"}:
        return value.lower() in {"1", "true", "yes", "on"}

    if key in {"POLL_INTERVAL", "ANALYTICS_WINDOW", "INGESTION_BATCH_SIZE"}:
        return int(value)

    return value


def load_env_values():
    env = {}

    for key, value in os.environ.items():
        if key in {
            "LOGEXP_ENV",
            "DATABASE_URL",
            "TIMEZONE",
            "START_POLLER",
            "POLL_INTERVAL",
            "GEIGER_DEVICE_PATH",
            "ANALYTICS_ENABLED",
            "ANALYTICS_WINDOW",
            "INGESTION_ENABLED",
            "INGESTION_BATCH_SIZE",
            "SHOW_DIAGNOSTICS",
            "SHOW_ANALYTICS",
        }:
            env[key] = coerce_value(key, value)

    return env
