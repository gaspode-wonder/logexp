import logging
import sys

def configure_logging(app):
    """Configure unified logging for LogExp."""

    # Clear default handlers (Flask adds one)
    app.logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Silence noisy libraries if needed
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
