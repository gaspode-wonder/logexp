from typing import Any

from flask import render_template

from logexp.app.bp.docs import bp_docs


@bp_docs.route("/")
def docs_index() -> Any:
    return render_template("docs.html")


@bp_docs.route("/timezone")
def timezone_policy() -> Any:
    return render_template("docs/timezone.html")
