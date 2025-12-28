from flask import Blueprint

bp_api = Blueprint("api", __name__, url_prefix="/api")

from . import routes  # noqa
