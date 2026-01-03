# filename: logexp/app/services/poller.py

from __future__ import annotations

from typing import Any, Dict, Optional

from flask import current_app


def get_poller_status() -> Dict[str, Optional[Any]]:
    """
    Service-layer poller diagnostics.

    Tests expect:
        - running: bool
        - last_tick: ISO8601 string or None
    """
    poller: Optional[Any] = getattr(current_app, "poller", None)

    if poller is None:
        return {
            "running": False,
            "last_tick": None,
        }

    # Determine running state
    thread = getattr(poller, "_thread", None)
    running: bool = bool(thread and thread.is_alive())

    # Determine last tick timestamp (if poller exposes it)
    last_tick_obj: Optional[Any] = getattr(poller, "last_tick", None)
    last_tick: Optional[str]

    if last_tick_obj is not None:
        try:
            last_tick = last_tick_obj.isoformat()
        except Exception:
            last_tick = None
    else:
        last_tick = None

    return {
        "running": running,
        "last_tick": last_tick,
    }
