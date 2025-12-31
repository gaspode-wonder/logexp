from flask import Blueprint, render_template

# Define a single blueprint for docs
bp_docs = Blueprint("docs", __name__, url_prefix="/docs")


@bp_docs.route("/")
def docs_index():
    """Render the docs index page."""
    return render_template("docs/docs.html")


@bp_docs.route("/timezone")
def timezone_policy():
    """Render the Timezone Policy page."""
    return render_template("docs/timezone.html")
