# filename: logexp/__init__.py

"""
Top-level package initializer for LogExp.

Configures structured logging immediately upon import so that all
logexp.* namespaces use consistent handlers and formatting.
"""

from __future__ import annotations

from logexp.app.logging_setup import configure_logging

# Configure logging at import time (tests, CLI, app factory)
configure_logging()
