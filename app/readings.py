# filename: logexp/app/readings.py
"""
DEPRECATED MODULE: readings.py

This file previously defined the 'readings_ui' and 'readings_api' blueprints.
All routes have been migrated into logexp/app/blueprints.py for consistency
and centralized registration.

Do not add new routes here. Please update or create routes only in
blueprints.py. This file remains temporarily for reference and will be
removed in a future release.
"""

from __future__ import annotations

import warnings

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.readings.deprecated")

logger.debug("deprecated_module_imported", extra={"module": "readings.py"})

warnings.warn(
    "readings.py is deprecated. Use logexp/app/blueprints.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
