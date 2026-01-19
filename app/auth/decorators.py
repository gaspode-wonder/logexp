# filename: app/auth/decorators.py

from __future__ import annotations

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import jsonify, session
from flask.typing import ResponseReturnValue

P = ParamSpec("P")
R = TypeVar("R")


def login_required(fn: Callable[P, R]) -> Callable[P, R | ResponseReturnValue]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | ResponseReturnValue:
        if "user_id" not in session:
            # jsonify returns a Response, so this is ResponseReturnValue
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)

    return wrapper
