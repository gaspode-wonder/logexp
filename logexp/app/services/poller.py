# logexp/app/services/poller.py

from __future__ import annotations

from flask import current_app


def get_poller_status() -> dict:
    """
    Service-layer poller diagnostics.

    Tests expect:
        - running: bool
        - last_tick: ISO8601 or None
    """

    poller = getattr(current_app, "poller", None)

    if poller is None:
        return {
            "running": False,
            "last_tick": None,
        }

    # Determine running state
    running = bool(getattr(poller, "_thread", None) and poller._thread.is_alive())

    # Determine last tick timestamp (if poller exposes it)
    last_tick = getattr(poller, "last_tick", None)
    if last_tick is not None:
        try:
            last_tick = last_tick.isoformat()
        except Exception:
            last_tick = None

    return {
        "running": running,
        "last_tick": last_tick,
    }
