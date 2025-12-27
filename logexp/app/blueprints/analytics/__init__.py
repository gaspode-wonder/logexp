from flask import Blueprint

bp_analytics = Blueprint("analytics", __name__, url_prefix="/analytics")

from . import routes  # noqa
