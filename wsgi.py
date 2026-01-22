# filename: wsgi.py

"""
WSGI entrypoint for LogExp.

Creates the application and conditionally starts the poller only when
running the actual server (not tests, not shell, not CLI).
"""

from __future__ import annotations

from logexp.app import create_app
from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.wsgi")

app = create_app()
logger.debug("wsgi_app_created")

# Start poller only when running the actual server (not tests, not shell)
if app.config_obj.get("START_POLLER", False):
    logger.debug("wsgi_poller_start_requested")

    from logexp.app.poller import GeigerPoller

    poller = GeigerPoller(app)
    poller.start()

    logger.info("wsgi_poller_started")
else:
    logger.debug("wsgi_poller_not_started", extra={"reason": "START_POLLER=False"})

if __name__ == "__main__":
    logger.info("wsgi_running_via_main")
    app.run()
