from logexp.app import create_app

app = create_app(
    {
        "TESTING": True,
        "START_POLLER": False,
    }
)

app.logger.info("demo log line")
