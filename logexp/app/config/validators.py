def validate_config(config):
    if config["POLL_INTERVAL"] <= 0:
        raise ValueError("POLL_INTERVAL must be > 0")

    if config["ANALYTICS_WINDOW"] <= 0:
        raise ValueError("ANALYTICS_WINDOW must be > 0")

    if config["INGESTION_BATCH_SIZE"] <= 0:
        raise ValueError("INGESTION_BATCH_SIZE must be > 0")

    if not isinstance(config["START_POLLER"], bool):
        raise ValueError("START_POLLER must be a boolean")

    return config