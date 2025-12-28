from flask import Blueprint

bp_docs = Blueprint("docs", __name__, url_prefix="/docs")

from . import routes  # noqa
