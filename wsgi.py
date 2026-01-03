# filename: wsgi.py

"""
WSGI entrypoint for LogExp.

Creates the application and conditionally starts the poller only when
running the actual server (not tests, not shell, not CLI).
"""

from __future__ import annotations

from logexp.app import create_app

app = create_app()

# Start poller only when running the actual server (not tests, not shell)
if app.config_obj.get("START_POLLER", False):
    from logexp.app.poller import GeigerPoller

    poller = GeigerPoller(app)
    poller.start()

if __name__ == "__main__":
    app.run()
