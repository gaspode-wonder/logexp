from flask import render_template
from . import bp_docs

# Placeholder: move docs routes from app_blueprints.py here.

@bp_docs.route("/timezone")
def timezone_policy():
    return render_template("docs/timezone.html")
