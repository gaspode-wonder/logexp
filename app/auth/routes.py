# filename: logexp/app/auth/routes.py

from flask import jsonify, request, session
from logexp.app.auth import bp_auth
from logexp.app.auth.decorators import login_required
from logexp.app.models import User


@bp_auth.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    # Step 1: allow union type here
    result = User.query.filter_by(username=username).first()

    # Step 2: eliminate the None branch
    if result is None:
        return jsonify({"error": "Invalid username or password"}), 401

    # Step 3: rebind to a concrete type
    user: User = result

    if not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Logged in", "user": user.username})


@bp_auth.post("/logout")
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


@bp_auth.get("/me")
@login_required
def me():
    user = User.query.get(session["user_id"])
    return jsonify({"username": user.username})
