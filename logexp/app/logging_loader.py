import logging

def configure_logging(app):
    """
    Configure application-wide logging.

    - Uses Python's built-in logging
    - Ensures logs go to stdout (Docker/Gunicorn friendly)
    - Respects Flask's debug level
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Flask's logger should use the same handlers
    app.logger.handlers = logging.getLogger().handlers
    app.logger.setLevel(logging.INFO)
