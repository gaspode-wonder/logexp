# filename: logexp/app/auth/__init__.py

from flask import Blueprint

# Canonical auth blueprint
bp_auth = Blueprint("auth", __name__, url_prefix="/auth")

# Attach routes
from . import routes  # noqa: E402, F401
