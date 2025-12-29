from flask import Blueprint

bp_health = Blueprint("health", __name__)

from . import routes  # noqa
