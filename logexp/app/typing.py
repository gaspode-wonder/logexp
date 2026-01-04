# filename: logexp/app/typing.py
from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Flask, Request


class LogExpFlask(Flask):
    """
    Typed Flask subclass declaring dynamic attributes added at runtime.
    """

    # Loaded config object (single source of truth)
    config_obj: Dict[str, Any]

    # Poller instance attached at runtime (optional)
    poller: Optional[Any]


class LogExpRequest(Request):
    """
    Typed Request subclass declaring dynamic attributes added by middleware.
    """

    request_id: Optional[str]
