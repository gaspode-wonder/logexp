# filename: app/auth/routes.py

from __future__ import annotations

from typing import Any, Tuple

from flask import jsonify, request
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app.auth import bp_auth
from app.extensions import db
from app.logging_setup import get_logger
from app.models import User  # adjust if your user model is named differently

logger = get_logger("beamfoundry.auth")


@bp_auth.post("/login")
def login() -> Tuple[Any, int]:
    logger.debug(
        "auth_login_requested",
        extra={"path": request.path, "method": request.method},
    )

    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        logger.debug("auth_login_missing_credentials")
        return jsonify({"error": "username and password required"}), 400

    user = db.session.query(User).filter_by(username=username).first()

    if user is None or not user.check_password(password):
        logger.debug(
            "auth_login_invalid_credentials",
            extra={"username": username},
        )
        return jsonify({"error": "invalid credentials"}), 401

    login_user(user)
    logger.debug(
        "auth_login_success",
        extra={"user_id": user.id, "username": user.username},
    )
    return jsonify({"status": "ok"}), 200


@bp_auth.post("/logout")
@login_required
def logout() -> Tuple[Any, int]:
    logger.debug(
        "auth_logout_requested",
        extra={"path": request.path, "method": request.method, "user_id": current_user.get_id()},
    )
    logout_user()
    logger.debug("auth_logout_success")
    return jsonify({"status": "logged_out"}), 200


@bp_auth.get("/me")
@login_required
def me() -> Tuple[Any, int]:
    logger.debug(
        "auth_me_requested",
        extra={"path": request.path, "method": request.method, "user_id": current_user.get_id()},
    )

    return (
        jsonify(
            {
                "id": current_user.id,
                "username": current_user.username,
            }
        ),
        200,
    )
