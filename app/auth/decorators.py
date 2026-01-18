# filename: logexp/app/auth/decorators.py

from functools import wraps

from flask import jsonify, session


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Explicit, deterministic check
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)

    return wrapper
