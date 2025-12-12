"""
DEPRECATED MODULE: logexp/app/blueprints/__init__.py

This file previously auto-imported and registered blueprints from multiple modules.
All blueprints are now centralized in logexp/app/blueprints.py.

⚠️ Do not use or import this file in the application factory.
It will be removed in a future release.
"""

import warnings
warnings.warn(
    "logexp/app/blueprints/__init__.py is deprecated. Use logexp/app/blueprints.py instead.",
    DeprecationWarning,
    stacklevel=2
)
