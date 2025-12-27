from flask import render_template
from . import bp_about

@bp_about.route("/")
def about_index():
    return render_template("info/about.html")
