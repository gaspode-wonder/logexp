from flask import Blueprint

bp_about = Blueprint("about", __name__, url_prefix="/about")

from . import routes  # noqa
