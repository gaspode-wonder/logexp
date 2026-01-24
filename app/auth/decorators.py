# filename: app/auth/decorators.py

from __future__ import annotations

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import jsonify

from ..auth.current_user import get_current_user

P = ParamSpec("P")
R = TypeVar("R")


def login_required(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401  # type: ignore[return-value]
        return fn(*args, **kwargs)

    return wrapper
