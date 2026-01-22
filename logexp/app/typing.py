# filename: logexp/app/typing.py
"""
Typed Flask and Request subclasses for LogExp.

This module declares the dynamic attributes that LogExp attaches to the
Flask application instance and the request object at runtime. These
attributes do not exist on the base Flask or Request classes, so mypy
must be informed explicitly.

Only attributes that are *actually added at runtime* should be declared
here. This keeps the typing surface minimal, accurate, and future‑proof.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Flask, Request


class LogExpFlask(Flask):
    """
    Typed Flask subclass for LogExp.

    Declares dynamic attributes assigned during application startup or
    runtime. These attributes are referenced throughout the codebase and
    must be visible to static type checkers.
    """

    #: Loaded configuration dictionary (single source of truth).
    #: Assigned in create_app() immediately after instantiation.
    config_obj: Dict[str, Any]

    #: Optional poller instance attached at runtime (tests, wsgi, CLI).
    #: Not always present, so typed as Optional[Any].
    poller: Optional[Any]


class LogExpRequest(Request):
    """
    Typed Request subclass for LogExp.

    Declares dynamic attributes added by request middleware. These
    attributes are attached per-request and must be visible to mypy.
    """

    #: Unique request identifier assigned by request_id_middleware().
    request_id: Optional[str]
