from flask import render_template, current_app, send_file
from . import bp_analytics

# Placeholder: move analytics routes from app_blueprints.py here.

@bp_analytics.route("/")
def analytics_index():
    return render_template("analytics.html")
