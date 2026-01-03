# logexp/app/bp/about/routes.py
from typing import Any

from flask import render_template

from logexp.app.bp.about import bp_about


@bp_about.route("/")
def about_index() -> Any:
    return render_template("about.html")
