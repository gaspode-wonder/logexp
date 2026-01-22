from flask import Blueprint

bp_settings = Blueprint("settings", __name__, url_prefix="/settings")

from . import routes  # noqa
