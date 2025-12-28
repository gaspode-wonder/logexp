from flask import Blueprint

bp_ui = Blueprint("ui", __name__)

from . import routes  # noqa
