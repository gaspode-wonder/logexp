# logexp/app/bp/diagnostics/__init__.py
from flask import Blueprint

bp_diagnostics = Blueprint("diagnostics", __name__, url_prefix="/diagnostics")

from . import routes  # noqa: F401, E402
