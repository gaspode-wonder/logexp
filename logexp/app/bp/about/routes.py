# logexp/app/bp/about/routes.py
from flask import render_template

from logexp.app.bp.about import bp_about


@bp_about.route("/")
def about_index():
    return render_template("about.html")
