from logexp.app import create_app
from logexp.app.config import TestConfig

app = create_app(TestConfig)
app.logger.info("demo log line")
