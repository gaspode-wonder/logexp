# logexp/app/bp/diagnostics_runtime/__init__.py
from __future__ import annotations

from flask import Blueprint

bp_diagnostics_runtime: Blueprint = Blueprint(
    name="diagnostics_runtime",
    import_name=__name__,
    url_prefix="/api/diagnostics/runtime",
)
