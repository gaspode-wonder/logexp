from flask import Blueprint

bp_diagnostics = Blueprint("diagnostics", __name__, url_prefix="/diagnostics")

from . import routes  # noqa
