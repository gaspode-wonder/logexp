# filename: app/auth/routes.py

from __future__ import annotations

from flask import jsonify, request, session
from flask.typing import ResponseReturnValue

from app.auth import bp_auth
from app.auth.decorators import login_required
from app.models import User


@bp_auth.post("/login")
def login() -> ResponseReturnValue:
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    # Query returns User | None
    result = User.query.filter_by(username=username).first()

    if result is None:
        return jsonify({"error": "Invalid username or password"}), 401

    user: User = result

    if not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Logged in", "user": user.username})


@bp_auth.post("/logout")
def logout() -> ResponseReturnValue:
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


@bp_auth.get("/me")
@login_required
def me() -> ResponseReturnValue:
    from app.auth.current_user import current_user

    user = current_user()
    assert user is not None  # login_required guarantees this

    return jsonify({"username": user.username})
